import logging
from decimal import Decimal
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class DepositRequirement:
    is_deposit_required: bool
    deposit_amount: Decimal
    reason: str | None
    checkout_url: str | None

class NoShowProtectionService:
    """Evaluates customer booking risk & enforces dynamic deposit requirements."""

    NO_SHOW_THRESHOLD = 2
    HIGH_VALUE_THRESHOLD = Decimal("50.00")
    DEFAULT_DEPOSIT = Decimal("10.00")

    def evaluate_booking_risk(
        self,
        customer_no_shows: int,
        service_price: Decimal,
        is_deposit_feature_enabled: bool = True,
    ) -> DepositRequirement:
        """Determines if a deposit is required before confirming slot."""
        if not is_deposit_feature_enabled:
            return DepositRequirement(is_deposit_required=False, deposit_amount=Decimal("0.00"), reason=None, checkout_url=None)

        if customer_no_shows >= self.NO_SHOW_THRESHOLD:
            reason = f"Customer has {customer_no_shows} past no-shows."
            deposit = min(self.DEFAULT_DEPOSIT, service_price)
            return DepositRequirement(
                is_deposit_required=True,
                deposit_amount=deposit,
                reason=reason,
                checkout_url=f"https://payriff.com/checkout/dep_{deposit}"
            )

        if service_price >= self.HIGH_VALUE_THRESHOLD:
            reason = f"High-value service booking ({service_price} AZN)."
            deposit = Decimal(str(round(float(service_price) * 0.20, 2)))  # 20% deposit
            return DepositRequirement(
                is_deposit_required=True,
                deposit_amount=deposit,
                reason=reason,
                checkout_url=f"https://epoint.az/checkout/dep_{deposit}"
            )

        return DepositRequirement(is_deposit_required=False, deposit_amount=Decimal("0.00"), reason=None, checkout_url=None)
