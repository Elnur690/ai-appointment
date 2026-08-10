import pytest
from uuid import uuid4
from datetime import date, datetime, timezone
from app.models.waitlist import WaitlistEntry, WaitlistStatus

def test_waitlist_model_creation():
    entry = WaitlistEntry(
        id=uuid4(),
        business_id=uuid4(),
        branch_id=uuid4(),
        customer_id=uuid4(),
        service_id=uuid4(),
        preferred_date=date(2026, 8, 15),
        status=WaitlistStatus.PENDING,
    )
    assert entry.status == WaitlistStatus.PENDING
    assert entry.preferred_date == date(2026, 8, 15)
