import pytest
from decimal import Decimal
from app.services.saas_analytics_service import SaaSAnalyticsService

def test_tenant_margin_calculation():
    margin = SaaSAnalyticsService.calculate_tenant_margin(
        business_id="b1",
        business_name="Beauty Studio Baku",
        plan_name="Pro Business",
        subscription_price=Decimal("100.00"),
        provider="gemini",
        total_tokens=50000,
    )
    assert margin.subscription_revenue == Decimal("100.00")
    assert margin.estimated_ai_cost == Decimal("0.01")  # 50k tokens * $0.0001/1k = $0.005 -> $0.01
    assert margin.net_profit > Decimal("99.00")
    assert margin.margin_percentage > 99.0
