import hashlib
import hmac
import logging
from decimal import Decimal
from uuid import UUID
import httpx

from app.core.config import settings
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult
from app.integrations.payments.fx import convert_to_usd

logger = logging.getLogger(__name__)


class CreemAdapter(PaymentAdapter):
    """Official Creem API v1 Adapter (https://docs.creem.io/api-reference/introduction)."""

    PROD_URL = "https://api.creem.io/v1"
    TEST_URL = "https://test-api.creem.io/v1"

    def _get_base_url(self, api_key: str, merchant_config: dict) -> str:
        if merchant_config.get("base_url"):
            return str(merchant_config["base_url"]).rstrip("/")
        if settings.CREEM_TEST_MODE or api_key.startswith("creem_test_"):
            return self.TEST_URL
        return self.PROD_URL

    async def create_payment_link(
        self,
        payment_id: UUID,
        amount: Decimal,
        currency: str,
        description: str,
        merchant_config: dict,
        return_url: str,
    ) -> PaymentLinkResult:
        api_key = (
            merchant_config.get("api_key")
            or merchant_config.get("creem_api_key")
            or settings.CREEM_API_KEY
            or ""
        ).strip()
        if not api_key:
            raise ValueError("CREEM_API_KEY is not configured")

        base_url = self._get_base_url(api_key, merchant_config)
        orig_currency = (currency or "AZN").strip().upper()
        usd_amount, fx_rate = await convert_to_usd(Decimal(str(amount)), orig_currency)
        price_cents = max(100, int((usd_amount * Decimal("100")).to_integral_value()))

        is_subscription = merchant_config.get("type") == "saas_subscription"
        product_payload: dict = {
            "name": (description or "Randevu.vip Payment")[:100],
            "description": description or "Randevu.vip Online Payment",
            "price": price_cents,
            "currency": "USD",
            "billing_type": "recurring" if is_subscription else "onetime",
        }
        if is_subscription:
            product_payload["billing_period"] = "every-month"

        headers = {
            "x-api-key": api_key,
            "Content-Type": "application/json",
        }

        extra_meta = {
            k: str(v)
            for k, v in merchant_config.items()
            if k in {"business_id", "appointment_id", "type", "plan_id"} and v is not None
        }

        async with httpx.AsyncClient(timeout=20.0) as client:
            prod_resp = await client.post(f"{base_url}/products", json=product_payload, headers=headers)
            if prod_resp.status_code not in (200, 201):
                logger.error(f"Creem POST /products failed ({prod_resp.status_code}): {prod_resp.text}")
                raise ValueError(f"Creem product creation failed ({prod_resp.status_code}): {prod_resp.text}")

            prod_data = prod_resp.json()
            product_id = prod_data.get("id")
            if not product_id:
                raise ValueError("Creem did not return a product id")

            checkout_payload = {
                "product_id": product_id,
                "request_id": str(payment_id),
                "success_url": return_url,
                "metadata": {
                    "paymentId": str(payment_id),
                    "originalAmount": f"{Decimal(str(amount)):.2f}",
                    "originalCurrency": orig_currency,
                    "usdAmount": f"{usd_amount:.2f}",
                    "fxRate": f"{fx_rate}",
                    **extra_meta,
                },
            }
            if merchant_config.get("customer_email"):
                checkout_payload["customer"] = {"email": merchant_config["customer_email"]}

            chk_resp = await client.post(f"{base_url}/checkouts", json=checkout_payload, headers=headers)
            if chk_resp.status_code not in (200, 201):
                logger.error(f"Creem POST /checkouts failed ({chk_resp.status_code}): {chk_resp.text}")
                raise ValueError(f"Creem checkout creation failed ({chk_resp.status_code}): {chk_resp.text}")

            chk_data = chk_resp.json()
            checkout_id = str(chk_data.get("id") or payment_id)
            checkout_url = chk_data.get("checkout_url")
            if not checkout_url:
                raise ValueError("Creem did not return checkout_url")

            return PaymentLinkResult(payment_url=checkout_url, transaction_id=checkout_id)

    async def verify_webhook(
        self,
        payload: dict,
        headers: dict,
        merchant_config: dict,
        raw_body: bytes | None = None,
    ) -> WebhookResult:
        """
        Verify Creem webhook using bare hex HMAC-SHA256 in `creem-signature` header over raw request body.
        Events: checkout.completed, subscription.active, subscription.paid,
                subscription.past_due, subscription.canceled, subscription.expired
        """
        webhook_secret = (
            merchant_config.get("webhook_secret")
            or merchant_config.get("creem_webhook_secret")
            or settings.CREEM_WEBHOOK_SECRET
            or ""
        ).strip()

        sig_header = (
            headers.get("creem-signature")
            or headers.get("Creem-Signature")
            or headers.get("CREEM-SIGNATURE")
            or ""
        ).strip()

        if webhook_secret and raw_body is not None:
            expected = hmac.new(
                webhook_secret.encode("utf-8"),
                raw_body,
                hashlib.sha256,
            ).hexdigest()
            if not sig_header or not hmac.compare_digest(expected, sig_header):
                logger.warning("Creem webhook signature verification failed")
                return WebhookResult(
                    transaction_id="",
                    is_successful=False,
                    amount=Decimal("0"),
                    raw_data=payload,
                )

        event_type = str(payload.get("eventType") or payload.get("type") or "").lower()
        obj = payload.get("object") if isinstance(payload.get("object"), dict) else payload
        tx_id = str(
            obj.get("id")
            or obj.get("checkout_id")
            or obj.get("request_id")
            or payload.get("id")
            or ""
        )

        # Creem amounts are in cents (integer)
        raw_amt = (
            obj.get("order", {}).get("amount")
            if isinstance(obj.get("order"), dict)
            else obj.get("amount")
        )
        try:
            amount = (Decimal(str(raw_amt)) / Decimal("100")).quantize(Decimal("0.01")) if raw_amt else Decimal("0.00")
        except Exception:
            amount = Decimal("0.00")

        is_success = event_type in {
            "checkout.completed",
            "subscription.active",
            "subscription.paid",
        }
        return WebhookResult(
            transaction_id=tx_id,
            is_successful=is_success,
            amount=amount,
            raw_data=payload,
        )

    async def check_status(self, transaction_id: str, merchant_config: dict) -> str:
        api_key = (merchant_config.get("api_key") or settings.CREEM_API_KEY or "").strip()
        if not api_key:
            return "pending"
        base_url = self._get_base_url(api_key, merchant_config)
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{base_url}/checkouts",
                    params={"checkout_id": transaction_id},
                    headers={"x-api-key": api_key},
                )
                if resp.status_code == 200:
                    status_val = str(resp.json().get("status") or "").lower()
                    return "completed" if status_val == "completed" else status_val
        except Exception as exc:
            logger.warning(f"Creem check_status error: {exc}")
        return "pending"

    async def create_recurring_product(self, name: str, amount: Decimal, currency: str = "AZN") -> str:
        """Create a monthly recurring Creem product and return its product_id."""
        api_key = (settings.CREEM_API_KEY or "").strip()
        if not api_key:
            raise ValueError("CREEM_API_KEY is not configured")
        base_url = self._get_base_url(api_key, {})
        usd_amount, _ = await convert_to_usd(Decimal(str(amount)), currency)
        price_cents = max(100, int((usd_amount * Decimal("100")).to_integral_value()))
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{base_url}/products",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={
                    "name": name[:100],
                    "description": f"{name} Monthly Plan",
                    "price": price_cents,
                    "currency": "USD",
                    "billing_type": "recurring",
                    "billing_period": "every-month",
                },
            )
            if resp.status_code not in (200, 201):
                raise ValueError(f"Creem product creation failed ({resp.status_code}): {resp.text}")
            return str(resp.json()["id"])

    async def upgrade_subscription(self, subscription_id: str, product_id: str) -> dict:
        """Upgrade or switch a Creem subscription via POST /v1/subscriptions/{id}/upgrade."""
        api_key = (settings.CREEM_API_KEY or "").strip()
        if not api_key:
            raise ValueError("CREEM_API_KEY is not configured")
        base_url = self._get_base_url(api_key, {})
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{base_url}/subscriptions/{subscription_id}/upgrade",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={"product_id": product_id, "update_behavior": "proration-charge-immediately"},
            )
            if resp.status_code not in (200, 201):
                raise ValueError(f"Creem subscription upgrade failed ({resp.status_code}): {resp.text}")
            return resp.json()

    async def cancel_subscription(self, subscription_id: str) -> dict:
        """Cancel a Creem subscription via POST /v1/subscriptions/{id}/cancel."""
        api_key = (settings.CREEM_API_KEY or "").strip()
        if not api_key:
            raise ValueError("CREEM_API_KEY is not configured")
        base_url = self._get_base_url(api_key, {})
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{base_url}/subscriptions/{subscription_id}/cancel",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
            )
            if resp.status_code not in (200, 201):
                raise ValueError(f"Creem subscription cancel failed ({resp.status_code}): {resp.text}")
            return resp.json()

    async def create_billing_portal_url(self, customer_id: str) -> str:
        """Create a Creem Customer Portal link via POST /v1/customers/billing."""
        api_key = (settings.CREEM_API_KEY or "").strip()
        if not api_key:
            raise ValueError("CREEM_API_KEY is not configured")
        base_url = self._get_base_url(api_key, {})
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{base_url}/customers/billing",
                headers={"x-api-key": api_key, "Content-Type": "application/json"},
                json={"customer_id": customer_id},
            )
            if resp.status_code not in (200, 201):
                raise ValueError(f"Creem billing portal failed ({resp.status_code}): {resp.text}")
            data = resp.json()
            return str(data.get("customer_portal_link") or data.get("url") or "")
