import pytest
from app.services.shift_schedule_service import ShiftScheduleService

def test_slot_within_morning_shift():
    service = ShiftScheduleService()
    result = service.validate_slot_within_shift(
        requested_date="2026-08-15",
        requested_time_str="10:00",
        service_duration_minutes=45,
        shift_type="morning"  # 09:00 - 15:00
    )
    assert result.is_valid is True
    assert result.is_overtime is False

def test_slot_outside_shift_no_overtime():
    service = ShiftScheduleService()
    result = service.validate_slot_within_shift(
        requested_date="2026-08-15",
        requested_time_str="16:00",
        service_duration_minutes=60,
        shift_type="morning",  # 09:00 - 15:00
        allow_overtime=False
    )
    assert result.is_valid is False
    assert "outside shift hours" in result.reason

def test_slot_outside_shift_approved_overtime():
    service = ShiftScheduleService()
    result = service.validate_slot_within_shift(
        requested_date="2026-08-15",
        requested_time_str="16:00",
        service_duration_minutes=60,
        shift_type="morning",  # 09:00 - 15:00
        allow_overtime=True
    )
    assert result.is_valid is True
    assert result.is_overtime is True
    assert "OVERTIME" in result.reason
