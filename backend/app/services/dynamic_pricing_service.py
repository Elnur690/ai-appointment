import logging
from dataclasses import dataclass
from decimal import Decimal
from datetime import datetime, time

logger = logging.getLogger(__name__)

@dataclass
class DynamicPricingRule:
    day_of_week: int  # 0=Monday to 6=Sunday
    start_time: time
    end_time: time
    multiplier: float  # e.g. 0.85 for 15% discount, 1.15 for 15% surge
    rule_name: str     # e.g. "Off-Peak Morning Discount", "Weekend Surge"

class DynamicPricingService:
    """Calculates time-based dynamic pricing adjustments for services."""
    
    DEFAULT_RULES = [
        # Off-peak weekday morning discount (Mon-Thu 09:00 - 12:00 -> 15% off)
        DynamicPricingRule(day_of_week=0, start_time=time(9, 0), end_time=time(12, 0), multiplier=0.85, rule_name="Off-Peak Morning Discount"),
        DynamicPricingRule(day_of_week=1, start_time=time(9, 0), end_time=time(12, 0), multiplier=0.85, rule_name="Off-Peak Morning Discount"),
        DynamicPricingRule(day_of_week=2, start_time=time(9, 0), end_time=time(12, 0), multiplier=0.85, rule_name="Off-Peak Morning Discount"),
        DynamicPricingRule(day_of_week=3, start_time=time(9, 0), end_time=time(12, 0), multiplier=0.85, rule_name="Off-Peak Morning Discount"),
        # Weekend peak surge (Fri-Sat 14:00 - 18:00 -> 15% surge)
        DynamicPricingRule(day_of_week=4, start_time=time(14, 0), end_time=time(18, 0), multiplier=1.15, rule_name="Weekend Peak Surge"),
        DynamicPricingRule(day_of_week=5, start_time=time(14, 0), end_time=time(18, 0), multiplier=1.15, rule_name="Weekend Peak Surge"),
    ]

    def calculate_price(
        self,
        base_price: Decimal,
        start_datetime: datetime,
        allows_dynamic_pricing: bool = True,
        custom_rules: list[DynamicPricingRule] | None = None,
    ) -> tuple[Decimal, str | None]:
        """
        Calculate final effective price for a service slot.
        Returns (effective_price, rule_applied_name).
        """
        if not allows_dynamic_pricing:
            return (base_price, None)

        rules = custom_rules or self.DEFAULT_RULES
        slot_day = start_datetime.weekday()
        slot_time = start_datetime.time()

        for rule in rules:
            if rule.day_of_week == slot_day and rule.start_time <= slot_time < rule.end_time:
                adjusted_price = Decimal(str(round(float(base_price) * rule.multiplier, 2)))
                return (adjusted_price, rule.rule_name)

        return (base_price, None)
