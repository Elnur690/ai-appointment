import pytest
from datetime import date, datetime, time, timezone
from uuid import uuid4
from app.services.availability_engine import AvailabilityEngine, AvailableSlot

def test_available_slot_serialization():
    slot = AvailableSlot(
        staff_id=uuid4(),
        staff_name="Dr. Alex Smith",
        start_time=datetime(2026, 8, 10, 10, 0, tzinfo=timezone.utc),
        end_time=datetime(2026, 8, 10, 10, 30, tzinfo=timezone.utc),
        service_id=uuid4(),
        service_name="Haircut & Styling",
    )
    data = slot.to_dict()
    assert data["staff_name"] == "Dr. Alex Smith"
    assert data["time"] == "10:00"
    assert data["date"] == "2026-08-10"

@pytest.mark.asyncio
async def test_availability_engine_initialization(db_session):
    engine = AvailabilityEngine(db=db_session)
    assert engine.SLOT_INCREMENT_MINUTES == 15
