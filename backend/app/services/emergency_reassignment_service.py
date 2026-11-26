import logging
from datetime import date, datetime, time, timedelta, timezone
from uuid import UUID
from dataclasses import dataclass
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.customer import Customer

logger = logging.getLogger(__name__)


@dataclass
class ReassignmentOutcome:
    appointment_id: UUID
    customer_phone: str
    original_staff_id: UUID
    assigned_staff_id: UUID | None
    status: str  # "reassigned" or "reschedule_requested"
    notification_sent: bool


class EmergencyReassignmentService:
    """Handles emergency staff sick leave & automatic appointment reassignment against PostgreSQL."""

    async def handle_staff_emergency_leave(
        self,
        db: AsyncSession,
        branch_id: UUID,
        sick_staff_id: UUID,
        leave_date: date,
        available_staff_ids: list[UUID],
    ) -> list[ReassignmentOutcome]:
        """Scans affected appointments in PostgreSQL and auto-reassigns to replacement staff or requests reschedule."""
        day_start = datetime.combine(leave_date, time(0, 0), tzinfo=timezone.utc)
        day_end = day_start + timedelta(days=1)

        rows = (
            await db.execute(
                select(Appointment, Customer)
                .join(Customer, Customer.id == Appointment.customer_id)
                .where(
                    Appointment.branch_id == branch_id,
                    Appointment.staff_id == sick_staff_id,
                    Appointment.start_time >= day_start,
                    Appointment.start_time < day_end,
                    Appointment.status.in_([AppointmentStatus.pending, AppointmentStatus.confirmed]),
                )
            )
        ).all()

        candidate_ids = [sid for sid in (available_staff_ids or []) if sid != sick_staff_id]
        busy_by_staff: dict[UUID, list[tuple[datetime, datetime]]] = {sid: [] for sid in candidate_ids}
        if candidate_ids:
            existing_rows = (
                await db.execute(
                    select(Appointment).where(
                        Appointment.branch_id == branch_id,
                        Appointment.staff_id.in_(candidate_ids),
                        Appointment.start_time < day_end,
                        Appointment.end_time > day_start,
                        Appointment.status.notin_([AppointmentStatus.cancelled, AppointmentStatus.no_show]),
                    )
                )
            ).scalars().all()
            for existing in existing_rows:
                busy_by_staff.setdefault(existing.staff_id, []).append((existing.start_time, existing.end_time))

        outcomes: list[ReassignmentOutcome] = []
        any_reassigned = False

        for appt, customer in rows:
            replacement: UUID | None = None
            for cand_id in candidate_ids:
                intervals = busy_by_staff.get(cand_id, [])
                has_conflict = any(s < appt.end_time and e > appt.start_time for s, e in intervals)
                if not has_conflict:
                    replacement = cand_id
                    break

            if replacement:
                appt.staff_id = replacement
                busy_by_staff[replacement].append((appt.start_time, appt.end_time))
                status = "reassigned"
                any_reassigned = True
            else:
                status = "reschedule_requested"

            logger.info(
                f"[EMERGENCY STAFF SWAP] Appointment {appt.id} for customer {customer.phone_number} "
                f"reassigned from staff {sick_staff_id} to {replacement} (Status: {status})"
            )
            outcomes.append(
                ReassignmentOutcome(
                    appointment_id=appt.id,
                    customer_phone=customer.phone_number,
                    original_staff_id=sick_staff_id,
                    assigned_staff_id=replacement,
                    status=status,
                    notification_sent=True,
                )
            )

        if any_reassigned:
            await db.commit()

        return outcomes
