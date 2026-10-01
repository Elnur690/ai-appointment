try:
    import pytest
except ImportError:
    pass
from datetime import date, timedelta
from uuid import uuid4
from app.services.gift_voucher_service import GiftVoucherService

def test_create_gift_voucher():
    service = GiftVoucherService()
    biz_id = uuid4()
    voucher = service.create_gift_voucher(
        business_id=biz_id,
        business_name="Beauty Studio Baku",
        sender_name="Leyla",
        recipient_name="Nigar",
        recipient_phone="+994501234567",
        amount_azn=100.0,
        greeting_message="Ad günün mübarək!",
        language="az",
        plan_allows_gift_vouchers=True,
    )

    assert voucher is not None
    assert voucher.code.startswith("GIFT-")
    assert voucher.amount_azn == 100.0
    assert "Nigar" in voucher.delivery_message
    assert "Leyla" in voucher.delivery_message
    assert "Ad günün mübarək!" in voucher.delivery_message
    assert "https://checkout.payriff.com" in voucher.payment_url

def test_redeem_gift_voucher_success():
    service = GiftVoucherService()
    biz_id = uuid4()
    voucher = service.create_gift_voucher(
        business_id=biz_id,
        business_name="Beauty Studio Baku",
        sender_name="Leyla",
        recipient_name="Nigar",
        recipient_phone="+994501234567",
        amount_azn=50.0,
        plan_allows_gift_vouchers=True,
    )
    # Simulate payment confirmed
    voucher.is_paid = True

    # Appointment total 80 AZN
    res = service.redeem_voucher(voucher, appointment_total_azn=80.0)
    assert res["success"] is True
    assert res["discount_azn"] == 50.0
    assert res["final_payable_azn"] == 30.0

def test_redeem_gift_voucher_unpaid_or_expired():
    service = GiftVoucherService()
    biz_id = uuid4()
    voucher = service.create_gift_voucher(
        business_id=biz_id,
        business_name="Beauty Studio Baku",
        sender_name="Leyla",
        recipient_name="Nigar",
        recipient_phone="+994501234567",
        amount_azn=50.0,
        plan_allows_gift_vouchers=True,
    )
    # Still unpaid
    res = service.redeem_voucher(voucher, appointment_total_azn=80.0)
    assert res["success"] is False
    assert "not been paid" in res["reason"]

    # Paid but expired
    voucher.is_paid = True
    voucher.expires_at = date(2025, 1, 1)
    res_expired = service.redeem_voucher(voucher, appointment_total_azn=80.0, current_date=date(2026, 1, 1))
    assert res_expired["success"] is False
    assert "expired" in res_expired["reason"]
