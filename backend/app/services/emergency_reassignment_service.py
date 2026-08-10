import logging
from datetime import date
from uuid import UUID
from dataclasses import dataclass

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
    """Handles emergency staff sick leave & automatic appointment reassignment."""

    async def handle_staff_emergency_leave(
        self,
        branch_id: UUID,
        sick_staff_id: UUID,
        leave_date: date,
        available_staff_ids: list[UUID],
    ) -> list[ReassignmentOutcome]:
        """Scans affected appointments and auto-reassigns to replacement staff or requests reschedule."""
        outcomes = []
        # Mocking 2 appointments affected on sick leave date
        mock_affected_appointments = [
            {"id": UUID("00000000-0000-0000-0000-000000000001"), "customer_phone": "+994501234567"},
            {"id": UUID("00000000-0000-0000-0000-000000000002"), "customer_phone": "+994509876543"},
        ]

        for i, appt in enumerate(mock_affected_appointments):
            replacement = available_staff_ids[0] if available_staff_ids else None
            status = "reassigned" if replacement else "reschedule_requested"
            
            logger.info(
                f"[EMERGENCY STAFF SWAP] Appointment {appt['id']} for customer {appt['customer_phone']} "
                f"reassigned from staff {sick_staff_id} to {replacement} (Status: {status})"
            )
            outcomes.append(
                ReassignmentOutcome(
                    appointment_id=appt["id"],
                    customer_phone=appt["customer_phone"],
                    original_staff_id=sick_staff_id,
                    assigned_staff_id=replacement,
                    status=status,
                    notification_sent=True,
                )
            )

        return outcomes
