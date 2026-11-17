import logging
from decimal import Decimal
from dataclasses import dataclass
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class DepositRequirement:
    is_deposit_required: bool
    deposit_amount: Decimal
    reason: str | None
    checkout_url: str | None = None


class NoShowProtectionService:
    """Evaluates customer booking risk & business-configured Beh (deposit) rules."""

    DEFAULT_NO_SHOW_THRESHOLD = 2
    DEFAULT_HIGH_VALUE_THRESHOLD = Decimal("50.00")
    DEFAULT_FIXED_DEPOSIT = Decimal("10.00")
    DEFAULT_PERCENTAGE = Decimal("20")
    DEFAULT_REGULAR_MIN_VISITS = 2

    def evaluate_booking_risk(
        self,
        customer_no_shows: int,
        service_price: Decimal,
        is_deposit_feature_enabled: bool = True,
        customer_completed_visits: int = 0,
        service_id: str | None = None,
        business_settings: dict[str, Any] | None = None,
    ) -> DepositRequirement:
        """
        Determines if a pre-payment (Beh) is required before confirming an appointment.

        - Master toggle (`is_deposit_feature_enabled`) is controlled by Platform Admin
          (Plan `allows_no_show_deposits` / Business entitlement).
        - Granular rules (who pays Beh, amount/percentage, regular customer exemption)
          are configured by each Business in Settings.
        """
        if not is_deposit_feature_enabled:
            return DepositRequirement(
                is_deposit_required=False,
                deposit_amount=Decimal("0.00"),
                reason=None,
                checkout_url=None,
            )

        cfg = business_settings or {}
        rule_mode = str(cfg.get("deposit_rule_mode") or "high_risk_only").strip().lower()
        min_service_price = Decimal(str(cfg.get("deposit_min_service_price") or self.DEFAULT_HIGH_VALUE_THRESHOLD))
        selected_service_ids = {str(sid) for sid in (cfg.get("deposit_service_ids") or []) if sid}
        calc_type = str(cfg.get("deposit_calc_type") or "percentage").strip().lower()
        percentage = Decimal(str(cfg.get("deposit_percentage") or self.DEFAULT_PERCENTAGE))
        fixed_amount = Decimal(str(cfg.get("deposit_fixed_amount") or self.DEFAULT_FIXED_DEPOSIT))
        skip_regular = bool(cfg.get("deposit_skip_regular_customers", True))
        regular_min_visits = int(cfg.get("deposit_regular_min_visits") or self.DEFAULT_REGULAR_MIN_VISITS)
        no_show_threshold = int(cfg.get("deposit_no_show_threshold") or self.DEFAULT_NO_SHOW_THRESHOLD)

        # 1. Regular / loyal customer exemption (if enabled by business)
        if skip_regular and customer_completed_visits >= regular_min_visits and customer_no_shows < no_show_threshold:
            return DepositRequirement(
                is_deposit_required=False,
                deposit_amount=Decimal("0.00"),
                reason=f"Regular customer exempted ({customer_completed_visits} completed visits).",
                checkout_url=None,
            )

        # 2. Evaluate trigger conditions
        reason: str | None = None
        if customer_no_shows >= no_show_threshold:
            reason = f"Customer has {customer_no_shows} past no-shows."
        elif rule_mode == "all":
            reason = "Pre-payment (Beh) required for all bookings per business policy."
        elif rule_mode == "above_amount" and service_price >= min_service_price:
            reason = f"Service price ({service_price:.2f} AZN) meets minimum threshold ({min_service_price:.2f} AZN)."
        elif rule_mode == "selected_services" and service_id and str(service_id) in selected_service_ids:
            reason = "Selected high-value service requires pre-payment (Beh)."

        if not reason:
            return DepositRequirement(
                is_deposit_required=False,
                deposit_amount=Decimal("0.00"),
                reason=None,
                checkout_url=None,
            )

        # 3. Compute deposit amount (never exceeding service price)
        if calc_type == "fixed":
            deposit = min(fixed_amount, service_price)
        else:
            deposit = (service_price * percentage / Decimal("100")).quantize(Decimal("0.01"))
            deposit = min(deposit, service_price)

        if deposit <= Decimal("0.00"):
            return DepositRequirement(
                is_deposit_required=False,
                deposit_amount=Decimal("0.00"),
                reason=None,
                checkout_url=None,
            )

        return DepositRequirement(
            is_deposit_required=True,
            deposit_amount=deposit,
            reason=reason,
            checkout_url=None,
        )
