try:
    import pytest
except ImportError:
    pass
from datetime import datetime, timedelta
from uuid import uuid4
from app.services.flash_drop_service import FlashDropService

def test_evaluate_flash_drop_within_window():
    service = FlashDropService()
    now = datetime(2026, 10, 1, 14, 0)
    slot_time = datetime(2026, 10, 1, 16, 0) # 2 hours away (within 0.5-4.5h window)

    offer = service.evaluate_cancellation_for_flash_drop(
        appointment_id=uuid4(),
        business_id=uuid4(),
        service_name="Balayage & Styling",
        staff_name="Leyla",
        slot_datetime=slot_time,
        original_price=100.0,
        current_time=now,
        discount_percentage=20,
        validity_minutes=25,
        language="az",
        plan_allows_flash_drops=True,
    )

    assert offer is not None
    assert offer.flash_price == 80.0
    assert offer.discount_percentage == 20
    assert offer.slot_time == "16:00"
    assert "QAYNAR TƏKLİF" in offer.broadcast_message
    assert "80.00 AZN" in offer.broadcast_message

def test_evaluate_flash_drop_outside_window():
    service = FlashDropService()
    now = datetime(2026, 10, 1, 10, 0)
    slot_time = datetime(2026, 10, 1, 18, 0) # 8 hours away (outside 0.5-4.5h window)

    offer = service.evaluate_cancellation_for_flash_drop(
        appointment_id=uuid4(),
        business_id=uuid4(),
        service_name="Balayage",
        staff_name="Leyla",
        slot_datetime=slot_time,
        original_price=100.0,
        current_time=now,
        plan_allows_flash_drops=True,
    )
    assert offer is None

def test_claim_flash_drop_atomic():
    service = FlashDropService()
    now = datetime(2026, 10, 1, 14, 0)
    slot_time = datetime(2026, 10, 1, 16, 0)

    offer = service.evaluate_cancellation_for_flash_drop(
        appointment_id=uuid4(),
        business_id=uuid4(),
        service_name="Haircut",
        staff_name="Elvin",
        slot_datetime=slot_time,
        original_price=50.0,
        current_time=now,
        validity_minutes=20,
        plan_allows_flash_drops=True,
    )

    client1 = uuid4()
    client2 = uuid4()

    # Client 1 claims first
    res1 = service.claim_flash_drop(offer, client_id=client1, claim_time=now + timedelta(minutes=5))
    assert res1["success"] is True
    assert offer.is_claimed is True
    assert offer.claimed_by_client_id == client1

    # Client 2 tries to claim same slot
    res2 = service.claim_flash_drop(offer, client_id=client2, claim_time=now + timedelta(minutes=6))
    assert res2["success"] is False
    assert res2["reason"] == "already_claimed"
