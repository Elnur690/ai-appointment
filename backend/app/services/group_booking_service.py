import logging
from dataclasses import dataclass
from uuid import UUID

logger = logging.getLogger(__name__)

@dataclass
class GroupBookingResult:
    group_size: int
    assigned_staff: list[dict]
    is_group_slot_available: bool
    status: str

class GroupBookingService:
    """Coordinates multi-person group & event bookings across staff members simultaneously."""

    def schedule_group_booking(
        self,
        group_size: int,
        requested_date: str,
        requested_time: str,
        available_staff: list[dict],
        allows_group: bool = True,
    ) -> GroupBookingResult:
        if not allows_group or len(available_staff) < group_size:
            return GroupBookingResult(
                group_size=group_size,
                assigned_staff=[],
                is_group_slot_available=False,
                status="Insufficient staff available for concurrent group booking.",
            )

        assigned = available_staff[:group_size]
        return GroupBookingResult(
            group_size=group_size,
            assigned_staff=assigned,
            is_group_slot_available=True,
            status=f"Successfully reserved {group_size} concurrent slots for {requested_date} at {requested_time}.",
        )
