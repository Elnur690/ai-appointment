import logging
from dataclasses import dataclass
from decimal import Decimal

logger = logging.getLogger(__name__)

@dataclass
class LoyaltyStatus:
    customer_id: str
    total_visits: int
    vip_tier: str  # "Bronze", "Silver", "Gold", "VIP Platinum"
    reward_unlocked: str | None
    discount_percentage: float

class LoyaltyService:
    """Manages AI Customer Loyalty & VIP Rewards Program."""

    def evaluate_customer_loyalty(self, customer_id: str, visit_count: int, allows_loyalty: bool = True) -> LoyaltyStatus:
        if not allows_loyalty:
            return LoyaltyStatus(customer_id=customer_id, total_visits=visit_count, vip_tier="Standard", reward_unlocked=None, discount_percentage=0.0)

        if visit_count >= 10:
            return LoyaltyStatus(
                customer_id=customer_id,
                total_visits=visit_count,
                vip_tier="VIP Platinum",
                reward_unlocked="Free Hair Treatment Voucher (10th Visit Milestone)",
                discount_percentage=15.0,
            )
        elif visit_count >= 5:
            return LoyaltyStatus(
                customer_id=customer_id,
                total_visits=visit_count,
                vip_tier="Gold",
                reward_unlocked="10% Discount on Next Booking (5th Visit Milestone)",
                discount_percentage=10.0,
            )
        else:
            return LoyaltyStatus(customer_id=customer_id, total_visits=visit_count, vip_tier="Bronze", reward_unlocked=None, discount_percentage=0.0)
