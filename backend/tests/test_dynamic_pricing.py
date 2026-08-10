import pytest
from decimal import Decimal
from datetime import datetime
from app.services.dynamic_pricing_service import DynamicPricingService

def test_off_peak_discount_calculation():
    service = DynamicPricingService()
    # Monday 10:00 AM (weekday morning -> 15% discount)
    mon_morning = datetime(2026, 8, 10, 10, 0)
    adjusted, rule = service.calculate_price(Decimal("30.00"), mon_morning, allows_dynamic_pricing=True)
    assert adjusted == Decimal("25.50")
    assert rule == "Off-Peak Morning Discount"

def test_weekend_surge_calculation():
    service = DynamicPricingService()
    # Friday 15:00 PM (weekend peak -> 15% surge)
    fri_afternoon = datetime(2026, 8, 14, 15, 0)
    adjusted, rule = service.calculate_price(Decimal("30.00"), fri_afternoon, allows_dynamic_pricing=True)
    assert adjusted == Decimal("34.50")
    assert rule == "Weekend Peak Surge"

def test_disabled_dynamic_pricing():
    service = DynamicPricingService()
    mon_morning = datetime(2026, 8, 10, 10, 0)
    adjusted, rule = service.calculate_price(Decimal("30.00"), mon_morning, allows_dynamic_pricing=False)
    assert adjusted == Decimal("30.00")
    assert rule is None
