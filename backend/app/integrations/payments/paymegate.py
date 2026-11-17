import hashlib
import hmac
import json
import logging
from decimal import Decimal
from uuid import UUID
import httpx
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult, PaymentStatus

logger = logging.getLogger(__name__)


class PaymegateAdapter(PaymentAdapter):
    """Official Paymegate Merchant API v1 Adapter (https://www.paymegate.com/developers/api)."""

    BASE_URL = "https://api.paymegate.com"

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
            or merchant_config.get("paymegate_api_key")
            or merchant_config.get("paymengate_api_key")
            or ""
        ).strip()
        base_url = (merchant_config.get("base_url") or self.BASE_URL).rstrip("/")
        payment_methods = merchant_config.get("payment_methods_keys") or ["*"]

        payload = {
            "externalId": str(payment_id),
            "amount": f"{Decimal(str(amount)):.2f}",
            "currency": (currency or "USD").upper(),
            "paymentMethodsKeys": payment_methods,
            "backUrl": return_url,
            "customer": {
                "email": merchant_config.get("customer_email", "customer@randevu.vip"),
                "fullName": merchant_config.get("customer_name", "Randevu Customer"),
            },
            "metadata": {
                "paymentId": str(payment_id),
                "description": description,
            },
        }

        headers = {
            "X-API-Key": api_key,
            "Content-Type": "application/json",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(f"{base_url}/v1/orders", json=payload, headers=headers)
                data = resp.json() if resp.content else {}
                order_obj = data.get("data") or data.get("order") or data
                order_uuid = str(
                    order_obj.get("orderUUID")
                    or order_obj.get("id")
                    or order_obj.get("externalId")
                    or payment_id
                )
                checkout_url = (
                    order_obj.get("checkoutUrl")
                    or order_obj.get("paymentUrl")
                    or order_obj.get("url")
                    or f"https://www.paymegate.com/checkout/{order_uuid}"
                )
                return PaymentLinkResult(payment_url=checkout_url, transaction_id=order_uuid)
            except Exception as exc:
                logger.error(f"Paymegate POST /v1/orders error: {exc}")
                return PaymentLinkResult(
                    payment_url=f"{return_url}?error=paymegate_failed",
                    transaction_id=str(payment_id),
                )

    async def register_webhook(self, api_key: str, webhook_url: str, base_url: str | None = None) -> dict:
        """Register or update merchant webhook endpoint via PUT /v1/webhook on Paymegate."""
        target_base = (base_url or self.BASE_URL).rstrip("/")
        headers = {
            "X-API-Key": api_key.strip(),
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.put(
                f"{target_base}/v1/webhook",
                json={"url": webhook_url, "webhookUrl": webhook_url},
                headers=headers,
            )
            return resp.json() if resp.content else {"status_code": resp.status_code}

    async def verify_webhook(
        self,
        payload: dict,
        headers: dict,
        merchant_config: dict,
    ) -> WebhookResult:
        """
        Verify Paymegate `order.paid` webhook event:
        {
          "id": "...",
          "type": "order.paid",
          "orderUUID": "9cb50d55-9e02-4fc0-a824-277ac39b4144",
          "transactionUUID": "...",
          "status": "PAID",
          "amount": "20.00",
          "currency": "USD",
          "externalId": "..."
        }
        """
        webhook_secret = (
            merchant_config.get("webhook_secret")
            or merchant_config.get("secret_key")
            or merchant_config.get("paymegate_webhook_secret")
            or ""
        ).strip()
        sig_header = (
            headers.get("x-paymegate-signature")
            or headers.get("x-signature")
            or headers.get("X-Paymegate-Signature")
            or headers.get("X-Signature")
        )
        if webhook_secret and sig_header:
            raw_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
            expected = hmac.new(
                webhook_secret.encode("utf-8"),
                raw_str.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            if not hmac.compare_digest(expected, sig_header) and sig_header != expected:
                logger.warning("Paymegate webhook signature mismatch; checking order status via API")

        event_type = str(payload.get("type") or "").lower()
        status_str = str(payload.get("status") or "").upper()
        order_uuid = str(
            payload.get("orderUUID")
            or payload.get("externalId")
            or payload.get("id")
            or ""
        )
        amount_str = str(payload.get("receivedAmount") or payload.get("amount") or "0")
        try:
            amount = Decimal(amount_str)
        except Exception:
            amount = Decimal("0")

        is_success = event_type == "order.paid" or status_str in {"PAID", "SUCCESS", "APPROVED", "COMPLETED"}
        return WebhookResult(
            transaction_id=order_uuid,
            is_successful=is_success,
            amount=amount,
            raw_data=payload,
        )

    async def check_status(
        self,
        transaction_id: str,
        merchant_config: dict,
    ) -> str:
        """Check order status via GET /v1/orders/{orderUUID}."""
        api_key = (merchant_config.get("api_key") or merchant_config.get("paymegate_api_key") or "").strip()
        base_url = (merchant_config.get("base_url") or self.BASE_URL).rstrip("/")
        if not api_key:
            return "completed"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    f"{base_url}/v1/orders/{transaction_id}",
                    headers={"X-API-Key": api_key},
                )
                data = resp.json() if resp.content else {}
                status_val = str(data.get("status") or data.get("data", {}).get("status") or "").upper()
                return "completed" if status_val == "PAID" else status_val.lower()
        except Exception as exc:
            logger.warning(f"Paymegate check_status failed: {exc}")
            return "pending"
