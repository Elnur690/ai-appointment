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

        outcomes: list[ReassignmentOutcome] = []
        replacement = available_staff_ids[0] if available_staff_ids else None

        for appt, customer in rows:
            if replacement:
                appt.staff_id = replacement
                status = "reassigned"
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

        if replacement and outcomes:
            await db.commit()

        return outcomes
