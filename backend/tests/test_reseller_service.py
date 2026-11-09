try:
    import pytest
except ImportError:
    pass

import asyncio
from uuid import uuid4
from app.services.reseller_service import ResellerService
from app.services.custom_domain_service import CustomDomainService


def test_reseller_referral_url_randevu_vip():
    service = ResellerService()
    url = service.build_referral_url("partner baku")
    assert url == "https://randevu.vip/register?ref=PARTNER-BAKU"

    wl_url = service.build_referral_url("partner baku", white_label_domain="agency.bakudigital.az")
    assert wl_url == "https://agency.bakudigital.az/register?ref=PARTNER-BAKU"


def test_reseller_commission_calculation():
    service = ResellerService()
    split = service.calculate_commission(subscription_amount_azn=100.0, commission_rate_percent=25.0)
    assert split["gross_amount_azn"] == 100.0
    assert split["reseller_commission_azn"] == 25.0
    assert split["saas_net_amount_azn"] == 75.0


def test_reseller_portfolio_evaluation():
    service = ResellerService()
    res_id = uuid4()
    businesses = [
        {"id": "b1", "name": "Salon A", "status": "active", "plan_price_azn": 79.0},
        {"id": "b2", "name": "Salon B", "status": "active", "plan_price_azn": 199.0},
        {"id": "b3", "name": "Salon C", "status": "suspended", "plan_price_azn": 79.0},
    ]
    summary = service.evaluate_reseller_portfolio(
        reseller_id=res_id,
        reseller_name="Kamran Əliyev",
        referral_code="PARTNER-BAKU",
        commission_rate_percent=20.0,
        referred_businesses=businesses,
        total_earned_historical_azn=300.0,
        total_paid_historical_azn=200.0,
        company_name="Baku Digital Agency",
    )

    assert summary.referred_businesses_count == 3
    assert summary.active_businesses_count == 2
    assert summary.total_mrr_generated_azn == 278.0
    assert summary.monthly_commission_azn == 55.6
    assert summary.saas_net_revenue_azn == 222.4
    assert summary.pending_payout_azn == 100.0


def test_custom_domain_cname_target_randevu_vip():
    service = CustomDomainService()
    res = asyncio.run(service.verify_and_provision_cname("Booking.BeautyStudio.az", uuid4()))
    assert res.custom_domain == "booking.beautystudio.az"
    assert res.cname_target == "cname.randevu.vip"
    assert res.is_cname_valid is True
    assert res.is_ssl_active is True
