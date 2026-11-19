import unittest
from decimal import Decimal

from app.services.no_show_protection_service import NoShowProtectionService
from app.integrations.payments.paymegate import PaymegateAdapter
from app.services.reseller_service import ResellerService


class TestProductionFlows(unittest.IsolatedAsyncioTestCase):
    def test_beh_disabled_by_admin_returns_false(self):
        svc = NoShowProtectionService()
        res = svc.evaluate_booking_risk(
            customer_no_shows=5,
            service_price=Decimal("200.00"),
            is_deposit_feature_enabled=False,
            customer_completed_visits=0,
            business_settings={"deposit_rule_mode": "all"},
        )
        self.assertFalse(res.is_deposit_required)
        self.assertEqual(res.deposit_amount, Decimal("0.00"))

    def test_beh_above_amount_percentage_and_regular_exemption(self):
        svc = NoShowProtectionService()
        settings = {
            "deposit_rule_mode": "above_amount",
            "deposit_min_service_price": 50,
            "deposit_calc_type": "percentage",
            "deposit_percentage": 20,
            "deposit_skip_regular_customers": True,
            "deposit_regular_min_visits": 2,
        }
        res_new = svc.evaluate_booking_risk(
            customer_no_shows=0,
            service_price=Decimal("100.00"),
            is_deposit_feature_enabled=True,
            customer_completed_visits=0,
            business_settings=settings,
        )
        self.assertTrue(res_new.is_deposit_required)
        self.assertEqual(res_new.deposit_amount, Decimal("20.00"))

        res_regular = svc.evaluate_booking_risk(
            customer_no_shows=0,
            service_price=Decimal("100.00"),
            is_deposit_feature_enabled=True,
            customer_completed_visits=3,
            business_settings=settings,
        )
        self.assertFalse(res_regular.is_deposit_required)

    def test_beh_selected_services_fixed_amount(self):
        svc = NoShowProtectionService()
        settings = {
            "deposit_rule_mode": "selected_services",
            "deposit_service_ids": ["svc-vip-1"],
            "deposit_calc_type": "fixed",
            "deposit_fixed_amount": 15,
            "deposit_skip_regular_customers": False,
        }
        res_match = svc.evaluate_booking_risk(
            customer_no_shows=0,
            service_price=Decimal("80.00"),
            is_deposit_feature_enabled=True,
            service_id="svc-vip-1",
            business_settings=settings,
        )
        self.assertTrue(res_match.is_deposit_required)
        self.assertEqual(res_match.deposit_amount, Decimal("15.00"))

        res_other = svc.evaluate_booking_risk(
            customer_no_shows=0,
            service_price=Decimal("80.00"),
            is_deposit_feature_enabled=True,
            service_id="svc-basic-2",
            business_settings=settings,
        )
        self.assertFalse(res_other.is_deposit_required)

    async def test_paymegate_order_paid_webhook_verification(self):
        adapter = PaymegateAdapter()
        payload = {
            "id": "evt-1",
            "type": "order.paid",
            "orderUUID": "3fa75c89-1eb6-42ac-8de6-2bede008d38c",
            "status": "PAID",
            "amount": "20.00",
            "currency": "AZN",
        }
        res = await adapter.verify_webhook(payload=payload, headers={}, merchant_config={})
        self.assertTrue(res.is_successful)
        self.assertEqual(res.transaction_id, "3fa75c89-1eb6-42ac-8de6-2bede008d38c")
        self.assertEqual(res.amount, Decimal("20.00"))

    def test_reseller_referral_code_normalization(self):
        rs = ResellerService()
        self.assertEqual(rs.normalize_referral_code("  Baku Agency 01! "), "BAKU-AGENCY-01")


if __name__ == "__main__":
    unittest.main()
