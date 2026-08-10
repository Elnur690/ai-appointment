import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class TenantProfitMargin:
    business_id: str
    business_name: str
    plan_name: str
    subscription_revenue: Decimal
    ai_tokens_used: int
    estimated_ai_cost: Decimal
    net_profit: Decimal
    margin_percentage: float

class SaaSAnalyticsService:
    """Calculates SaaS Owner profit margins, token costs, and tenant unit economics."""

    # Estimated provider costs per 1k tokens
    TOKEN_COST_MAP = {
        "gemini": Decimal("0.0001"),    # ~$0.10 / 1M tokens
        "claude": Decimal("0.0030"),    # ~$3.00 / 1M tokens
        "openai": Decimal("0.0025"),    # ~$2.50 / 1M tokens
    }

    @classmethod
    def calculate_tenant_margin(
        self,
        business_id: str,
        business_name: str,
        plan_name: str,
        subscription_price: Decimal,
        provider: str,
        total_tokens: int,
    ) -> TenantProfitMargin:
        cost_per_token = self.TOKEN_COST_MAP.get(provider.lower(), Decimal("0.0001"))
        estimated_cost = Decimal(str(round(float((Decimal(total_tokens) / Decimal(1000)) * cost_per_token), 2)))
        net_profit = subscription_price - estimated_cost
        margin_pct = round(float((net_profit / subscription_price) * Decimal(100)), 1) if subscription_price > 0 else 0.0

        return TenantProfitMargin(
            business_id=business_id,
            business_name=business_name,
            plan_name=plan_name,
            subscription_revenue=subscription_price,
            ai_tokens_used=total_tokens,
            estimated_ai_cost=estimated_cost,
            net_profit=net_profit,
            margin_percentage=margin_pct,
        )
