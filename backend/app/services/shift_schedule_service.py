import logging
from datetime import datetime, time
from dataclasses import dataclass
from uuid import UUID

logger = logging.getLogger(__name__)

@dataclass
class ShiftValidationResult:
    is_valid: bool
    reason: str
    shift_name: str
    is_overtime: bool
    shift_start: str
    shift_end: str

class ShiftScheduleService:
    """Manages staff and solo-owner shifts (Morning, Evening, Full-Day, Custom) and enforces overtime rules."""

    SHIFT_PRESETS = {
        "morning": (time(9, 0), time(15, 0)),
        "evening": (time(15, 0), time(21, 0)),
        "full_day": (time(9, 0), time(21, 0)),
    }

    def validate_slot_within_shift(
        self,
        requested_date: str,
        requested_time_str: str,
        service_duration_minutes: int,
        shift_type: str = "full_day",
        custom_shift_start: time | None = None,
        custom_shift_end: time | None = None,
        allow_overtime: bool = False,
        plan_allows_shift_management: bool = True,
    ) -> ShiftValidationResult:
        """Validates whether a requested booking slot falls within assigned staff/owner shift hours if plan permits."""
        if not plan_allows_shift_management:
            logger.info("[PLAN GATED] Shift management not enabled on plan. Defaulting to open business hours.")
            return ShiftValidationResult(
                is_valid=True,
                reason="Shift management not enabled on plan; open hours apply.",
                shift_name="Standard Open Hours",
                is_overtime=False,
                shift_start="09:00",
                shift_end="21:00",
            )

        try:
            req_time = datetime.strptime(requested_time_str, "%H:%M").time()
            req_minutes = req_time.hour * 60 + req_time.minute
            end_minutes = req_minutes + service_duration_minutes
            req_end_time = time(end_minutes // 60, end_minutes % 60)

            if shift_type in self.SHIFT_PRESETS:
                s_start, s_end = self.SHIFT_PRESETS[shift_type]
            elif custom_shift_start and custom_shift_end:
                s_start, s_end = custom_shift_start, custom_shift_end
            else:
                s_start, s_end = self.SHIFT_PRESETS["full_day"]

            s_start_min = s_start.hour * 60 + s_start.minute
            s_end_min = s_end.hour * 60 + s_end.minute

            is_within = (req_minutes >= s_start_min) and (end_minutes <= s_end_min)

            if is_within:
                return ShiftValidationResult(
                    is_valid=True,
                    reason="Slot is within shift hours.",
                    shift_name=shift_type.replace("_", " ").title(),
                    is_overtime=False,
                    shift_start=s_start.strftime("%H:%M"),
                    shift_end=s_end.strftime("%H:%M"),
                )

            if allow_overtime:
                logger.warning(
                    f"[SHIFT OVERTIME] Booking at {requested_time_str} ({service_duration_minutes}m) "
                    f"approved as OVERTIME outside shift bounds {s_start.strftime('%H:%M')}-{s_end.strftime('%H:%M')}"
                )
                return ShiftValidationResult(
                    is_valid=True,
                    reason="Slot approved as OVERTIME extension.",
                    shift_name=f"{shift_type.replace('_', ' ').title()} (Overtime)",
                    is_overtime=True,
                    shift_start=s_start.strftime("%H:%M"),
                    shift_end=s_end.strftime("%H:%M"),
                )

            return ShiftValidationResult(
                is_valid=False,
                reason=f"Requested slot {requested_time_str} is outside shift hours ({s_start.strftime('%H:%M')}-{s_end.strftime('%H:%M')}).",
                shift_name=shift_type.replace("_", " ").title(),
                is_overtime=False,
                shift_start=s_start.strftime("%H:%M"),
                shift_end=s_end.strftime("%H:%M"),
            )

        except Exception as e:
            logger.error(f"Error validating shift schedule: {e}")
            return ShiftValidationResult(
                is_valid=False,
                reason="Invalid time format or shift calculation error.",
                shift_name=shift_type,
                is_overtime=False,
                shift_start="09:00",
                shift_end="18:00",
            )
