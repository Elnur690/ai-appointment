import logging
import re
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


@dataclass
class ResellerCommissionSummary:
    reseller_id: UUID
    reseller_name: str
    company_name: Optional[str]
    referral_code: str
    referral_url: str
    commission_rate_percent: float
    referred_businesses_count: int
    active_businesses_count: int
    total_mrr_generated_azn: float
    monthly_commission_azn: float
    saas_net_revenue_azn: float
    total_earned_azn: float
    total_paid_azn: float
    pending_payout_azn: float
    white_label_domain: Optional[str]


class ResellerService:
    """Manages SaaS Reseller / Agency Partners, referral attribution, white-label domains, and recurring commissions on randevu.vip."""

    BASE_DOMAIN = "randevu.vip"

    def normalize_referral_code(self, code_or_name: str) -> str:
        """Generates a clean uppercase referral code."""
        cleaned = re.sub(r"[^A-Za-z0-9_-]", "", code_or_name.upper().replace(" ", "-"))
        return cleaned[:32] if cleaned else f"PARTNER-{str(uuid4())[:6].upper()}"

    def build_referral_url(self, referral_code: str, white_label_domain: Optional[str] = None) -> str:
        """Builds the partner signup referral link on randevu.vip or partner white-label domain."""
        code = self.normalize_referral_code(referral_code)
        if white_label_domain:
            domain = white_label_domain.strip().lower()
            return f"https://{domain}/register?ref={code}"
        return f"https://{self.BASE_DOMAIN}/register?ref={code}"

    def calculate_commission(
        self,
        subscription_amount_azn: float,
        commission_rate_percent: float = 20.0,
    ) -> Dict[str, float]:
        """Calculates reseller commission and net SaaS revenue for a subscription payment."""
        if subscription_amount_azn <= 0 or commission_rate_percent < 0:
            return {
                "gross_amount_azn": max(0.0, subscription_amount_azn),
                "commission_rate_percent": max(0.0, commission_rate_percent),
                "reseller_commission_azn": 0.0,
                "saas_net_amount_azn": max(0.0, subscription_amount_azn),
            }

        capped_rate = min(commission_rate_percent, 80.0)
        commission = round(subscription_amount_azn * (capped_rate / 100.0), 2)
        net_saas = round(subscription_amount_azn - commission, 2)

        return {
            "gross_amount_azn": round(subscription_amount_azn, 2),
            "commission_rate_percent": capped_rate,
            "reseller_commission_azn": commission,
            "saas_net_amount_azn": net_saas,
        }

    def evaluate_reseller_portfolio(
        self,
        reseller_id: UUID,
        reseller_name: str,
        referral_code: str,
        commission_rate_percent: float,
        referred_businesses: List[Dict[str, Any]],
        total_earned_historical_azn: float = 0.0,
        total_paid_historical_azn: float = 0.0,
        company_name: Optional[str] = None,
        white_label_domain: Optional[str] = None,
    ) -> ResellerCommissionSummary:
        """Computes full financial & portfolio metrics for a reseller partner."""
        norm_code = self.normalize_referral_code(referral_code)
        ref_url = self.build_referral_url(norm_code, white_label_domain)

        active_count = 0
        total_mrr = 0.0
        monthly_comm = 0.0

        for biz in referred_businesses:
            status = str(biz.get("status", "active")).lower()
            plan_price = float(biz.get("plan_price_azn", 0.0))
            if status == "active":
                active_count += 1
                total_mrr += plan_price
                split = self.calculate_commission(plan_price, commission_rate_percent)
                monthly_comm += split["reseller_commission_azn"]

        total_mrr = round(total_mrr, 2)
        monthly_comm = round(monthly_comm, 2)
        saas_net = round(total_mrr - monthly_comm, 2)

        effective_earned = round(max(total_earned_historical_azn, monthly_comm), 2)
        pending_payout = round(max(0.0, effective_earned - total_paid_historical_azn), 2)

        return ResellerCommissionSummary(
            reseller_id=reseller_id,
            reseller_name=reseller_name,
            company_name=company_name,
            referral_code=norm_code,
            referral_url=ref_url,
            commission_rate_percent=commission_rate_percent,
            referred_businesses_count=len(referred_businesses),
            active_businesses_count=active_count,
            total_mrr_generated_azn=total_mrr,
            monthly_commission_azn=monthly_comm,
            saas_net_revenue_azn=saas_net,
            total_earned_azn=effective_earned,
            total_paid_azn=round(total_paid_historical_azn, 2),
            pending_payout_azn=pending_payout,
            white_label_domain=white_label_domain,
        )
