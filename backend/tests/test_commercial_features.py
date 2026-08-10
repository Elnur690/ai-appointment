import pytest
from decimal import Decimal
from app.services.loyalty_service import LoyaltyService
from app.services.combo_package_service import ComboPackageService
from app.services.group_booking_service import GroupBookingService
from app.services.product_upsell_service import ProductUpsellService

def test_loyalty_service_milestone():
    service = LoyaltyService()
    status_5 = service.evaluate_customer_loyalty("c1", visit_count=5)
    assert status_5.vip_tier == "Gold"
    assert status_5.discount_percentage == 10.0

    status_10 = service.evaluate_customer_loyalty("c1", visit_count=10)
    assert status_10.vip_tier == "VIP Platinum"
    assert status_10.discount_percentage == 15.0

def test_combo_package_service():
    service = ComboPackageService()
    items = [
        {"name": "Haircut", "duration": 45, "price": 30},
        {"name": "Beard Trim", "duration": 30, "price": 15},
    ]
    res = service.calculate_combo_package(items, allows_combo=True)
    assert res.total_duration_minutes == 75
    assert res.original_total_price == Decimal("45")
    assert res.combo_discounted_price == Decimal("38.25")  # 15% discount off 45 = 38.25

def test_group_booking_service():
    service = GroupBookingService()
    staff_list = [{"id": "s1", "name": "Alice"}, {"id": "s2", "name": "Bob"}, {"id": "s3", "name": "Charlie"}]
    res = service.schedule_group_booking(group_size=2, requested_date="2026-08-15", requested_time="11:00", available_staff=staff_list)
    assert res.is_group_slot_available is True
    assert len(res.assigned_staff) == 2

def test_product_upsell_service():
    service = ProductUpsellService()
    upsell = service.get_upsell_recommendation("haircut", allows_upsell=True)
    assert upsell is not None
    assert upsell.product_name == "Organic Argan Hair & Scalp Oil"
    assert upsell.price == Decimal("25.00")
