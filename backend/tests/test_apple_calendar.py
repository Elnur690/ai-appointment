import pytest
from datetime import datetime
from app.services.apple_calendar_service import AppleCalendarService

def test_apple_caldav_ics_generator():
    service = AppleCalendarService()
    start = datetime(2026, 8, 15, 10, 0)
    end = datetime(2026, 8, 15, 11, 0)
    
    ics = service._generate_vevent_ics(
        event_uid="test-uid-123",
        summary="Haircut Booking",
        start_time=start,
        end_time=end,
        description="Customer: Aysel",
    )
    
    assert "BEGIN:VCALENDAR" in ics
    assert "BEGIN:VEVENT" in ics
    assert "UID:test-uid-123" in ics
    assert "SUMMARY:Haircut Booking" in ics
    assert "20260815T100000Z" in ics
