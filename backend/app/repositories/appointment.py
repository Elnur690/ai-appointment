from datetime import datetime, date, time
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.repositories.base import BaseRepository
from app.models.appointment import Appointment, AppointmentStatus
from app.utils.timezone import to_utc

class AppointmentRepository(BaseRepository[Appointment]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Appointment, session, business_id)
        
    async def get_by_branch_and_date_range(self, branch_id: UUID, start: datetime, end: datetime) -> list[Appointment]:
        stmt = self._scoped_query().where(
            Appointment.branch_id == branch_id,
            Appointment.start_time >= start,
            Appointment.start_time <= end
        ).options(selectinload(Appointment.service), selectinload(Appointment.staff), selectinload(Appointment.customer))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_staff_and_date_range(self, staff_id: UUID, start: datetime, end: datetime) -> list[Appointment]:
        stmt = self._scoped_query().where(
            Appointment.staff_id == staff_id,
            Appointment.start_time >= start,
            Appointment.start_time <= end
        ).options(selectinload(Appointment.service), selectinload(Appointment.customer))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_customer(self, customer_id: UUID, limit: int = 10) -> list[Appointment]:
        stmt = self._scoped_query().where(
            Appointment.customer_id == customer_id
        ).order_by(Appointment.start_time.desc()).limit(limit).options(selectinload(Appointment.service), selectinload(Appointment.staff))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_upcoming_by_customer(self, customer_id: UUID) -> list[Appointment]:
        now = datetime.utcnow()
        stmt = self._scoped_query().where(
            Appointment.customer_id == customer_id,
            Appointment.start_time >= now,
            Appointment.status.notin_([AppointmentStatus.CANCELLED, AppointmentStatus.COMPLETED])
        ).order_by(Appointment.start_time.asc()).options(selectinload(Appointment.service), selectinload(Appointment.staff))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_today_appointments(self, branch_id: UUID, timezone: str) -> list[Appointment]:
        # Simple approximation, in a real scenario would use DB TZ functions or local calculation
        now = datetime.utcnow()
        today = now.date()
        start = to_utc(datetime.combine(today, time.min), timezone)
        end = to_utc(datetime.combine(today, time.max), timezone)
        return await self.get_by_branch_and_date_range(branch_id, start, end)
        
    async def update_status(self, appointment_id: UUID, status: AppointmentStatus) -> Appointment | None:
        appointment = await self.get_by_id(appointment_id)
        if appointment:
            appointment.status = status
            await self.session.flush()
        return appointment
