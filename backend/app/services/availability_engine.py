from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from uuid import UUID
from sqlalchemy import select, and_, or_
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.appointment import Appointment, AppointmentStatus
from app.models.staff import Staff, StaffSchedule, StaffService
from app.models.service import Service
from app.models.business import Branch
from app.utils.timezone import get_day_of_week, get_current_time, to_utc, from_utc

@dataclass
class AvailableSlot:
    staff_id: UUID
    staff_name: str
    start_time: datetime  # UTC
    end_time: datetime    # UTC
    service_id: UUID
    service_name: str
    
    def to_dict(self) -> dict:
        return {
            'staff_id': str(self.staff_id),
            'staff_name': self.staff_name,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat(),
            'date': self.start_time.strftime('%Y-%m-%d'),
            'time': self.start_time.strftime('%H:%M'),
        }

class AvailabilityEngine:
    """Core availability calculation engine. Single source of truth for slot availability."""
    
    SLOT_INCREMENT_MINUTES = 15  # Generate slots at 15-minute intervals
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_available_slots(
        self,
        branch_id: UUID,
        service_id: UUID,
        target_date: date,
        staff_id: UUID | None = None,
    ) -> list[AvailableSlot]:
        """Get all available time slots for a service on a given date."""
        service = await self._get_service(service_id)
        if not service:
            return []
        
        branch = await self._get_branch(branch_id)
        if not branch:
            return []
        
        day_of_week = target_date.weekday()
        
        branch_hours = self._get_branch_hours_for_day(branch.working_hours, day_of_week)
        if not branch_hours:
            return []
        
        eligible_staff = await self._get_eligible_staff(branch_id, service_id, staff_id)
        if not eligible_staff:
            return []
        
        all_slots = []
        for staff_member in eligible_staff:
            staff_schedule = await self._get_staff_schedule(staff_member.id, day_of_week)
            if not staff_schedule:
                continue
            
            work_start = max(branch_hours['start'], staff_schedule.start_time)
            work_end = min(branch_hours['end'], staff_schedule.end_time)
            
            if work_start >= work_end:
                continue
            
            existing_appointments = await self._get_existing_appointments(
                staff_member.id, target_date, branch.timezone
            )
            
            slots = self._generate_slots(
                staff_member=staff_member,
                service=service,
                target_date=target_date,
                work_start=work_start,
                work_end=work_end,
                existing_appointments=existing_appointments,
                timezone=branch.timezone,
            )
            all_slots.extend(slots)
        
        all_slots.sort(key=lambda s: (s.start_time, s.staff_name))
        return all_slots
    
    async def is_slot_available(
        self,
        branch_id: UUID,
        staff_id: UUID,
        service_id: UUID,
        start_time: datetime,
    ) -> bool:
        """Quick check if a specific slot is available."""
        service = await self._get_service(service_id)
        if not service:
            return False
        
        end_time = start_time + timedelta(minutes=service.duration_minutes)
        buffer = timedelta(minutes=service.buffer_minutes)
        
        branch = await self._get_branch(branch_id)
        if not branch:
            return False
        
        local_start = from_utc(start_time, branch.timezone)
        day_of_week = local_start.weekday()
        branch_hours = self._get_branch_hours_for_day(branch.working_hours, day_of_week)
        if not branch_hours:
            return False
        
        local_start_time = local_start.time()
        local_end_time = from_utc(end_time, branch.timezone).time()
        
        if local_start_time < branch_hours['start'] or local_end_time > branch_hours['end']:
            return False
        
        staff_schedule = await self._get_staff_schedule(staff_id, day_of_week)
        if not staff_schedule:
            return False
        if local_start_time < staff_schedule.start_time or local_end_time > staff_schedule.end_time:
            return False
        
        has_conflict = await self._check_appointment_conflict(
            staff_id, start_time - buffer, end_time + buffer
        )
        return not has_conflict
    
    async def get_next_available(
        self,
        branch_id: UUID,
        service_id: UUID,
        after: datetime,
        staff_id: UUID | None = None,
        limit: int = 5,
        max_days_ahead: int = 14,
    ) -> list[AvailableSlot]:
        """Find the next N available slots searching forward in time."""
        slots = []
        branch = await self._get_branch(branch_id)
        if not branch:
            return []
        
        current_date = from_utc(after, branch.timezone).date()
        end_date = current_date + timedelta(days=max_days_ahead)
        
        while current_date <= end_date and len(slots) < limit:
            day_slots = await self.get_available_slots(
                branch_id, service_id, current_date, staff_id
            )
            day_slots = [s for s in day_slots if s.start_time > after]
            slots.extend(day_slots)
            current_date += timedelta(days=1)
        
        return slots[:limit]

    async def _get_service(self, service_id: UUID) -> Service | None:
        stmt = select(Service).where(Service.id == service_id, Service.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
        
    async def _get_branch(self, branch_id: UUID) -> Branch | None:
        stmt = select(Branch).where(Branch.id == branch_id, Branch.is_active == True)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
        
    def _get_branch_hours_for_day(self, working_hours: dict, day_of_week: int) -> dict | None:
        if not working_hours:
            return None
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        day_str = days[day_of_week]
        
        hours = working_hours.get(day_str)
        if not hours:
            return None
        
        start_str = hours.get("start")
        end_str = hours.get("end")
        if not start_str or not end_str:
            return None
            
        def parse_time(t_str):
            h, m = map(int, t_str.split(':'))
            return time(h, m)
            
        return {
            "start": parse_time(start_str),
            "end": parse_time(end_str)
        }

    async def _get_eligible_staff(self, branch_id: UUID, service_id: UUID, staff_id: UUID | None) -> list[Staff]:
        stmt = select(Staff).join(StaffService).where(
            Staff.branch_id == branch_id,
            Staff.is_active == True,
            StaffService.service_id == service_id
        )
        if staff_id:
            stmt = stmt.where(Staff.id == staff_id)
            
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def _get_staff_schedule(self, staff_id: UUID, day_of_week: int) -> StaffSchedule | None:
        stmt = select(StaffSchedule).where(
            StaffSchedule.staff_id == staff_id,
            StaffSchedule.day_of_week == day_of_week
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def _get_existing_appointments(self, staff_id: UUID, target_date: date, timezone: str) -> list[Appointment]:
        start_dt = datetime.combine(target_date, time.min)
        end_dt = datetime.combine(target_date, time.max)
        
        utc_start = to_utc(start_dt, timezone)
        utc_end = to_utc(end_dt, timezone)
        
        stmt = select(Appointment).options(selectinload(Appointment.service)).where(
            Appointment.staff_id == staff_id,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
            Appointment.start_time < utc_end,
            Appointment.end_time > utc_start
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    def _generate_slots(
        self,
        staff_member: Staff,
        service: Service,
        target_date: date,
        work_start: time,
        work_end: time,
        existing_appointments: list[Appointment],
        timezone: str,
    ) -> list[AvailableSlot]:
        slots = []
        
        current_time_dt = datetime.combine(target_date, work_start)
        end_time_dt = datetime.combine(target_date, work_end)
        
        duration = timedelta(minutes=service.duration_minutes)
        buffer = timedelta(minutes=service.buffer_minutes)
        total_needed = duration + buffer
        
        while current_time_dt + duration <= end_time_dt:
            slot_start_utc = to_utc(current_time_dt, timezone)
            slot_end_utc = slot_start_utc + duration
            slot_buffered_end_utc = slot_start_utc + total_needed
            slot_buffered_start_utc = slot_start_utc - buffer
            
            conflict = False
            for appt in existing_appointments:
                appt_buffer = timedelta(minutes=appt.service.buffer_minutes if appt.service else 0)
                appt_buffered_start = appt.start_time - appt_buffer
                appt_buffered_end = appt.end_time + appt_buffer
                
                if max(slot_buffered_start_utc, appt_buffered_start) < min(slot_buffered_end_utc, appt_buffered_end):
                    conflict = True
                    break
                    
            if not conflict:
                slots.append(AvailableSlot(
                    staff_id=staff_member.id,
                    staff_name=staff_member.name,
                    start_time=slot_start_utc,
                    end_time=slot_end_utc,
                    service_id=service.id,
                    service_name=service.name
                ))
                
            current_time_dt += timedelta(minutes=self.SLOT_INCREMENT_MINUTES)
            
        return slots

    async def _check_appointment_conflict(self, staff_id: UUID, buffered_start: datetime, buffered_end: datetime) -> bool:
        stmt = select(Appointment).where(
            Appointment.staff_id == staff_id,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.NO_SHOW]),
            Appointment.start_time < buffered_end,
            Appointment.end_time > buffered_start
        )
        result = await self.db.execute(stmt)
        return result.first() is not None
