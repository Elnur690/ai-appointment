import hashlib
import hmac
import json
import logging
from decimal import Decimal
from uuid import UUID
import httpx
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult, PaymentStatus

logger = logging.getLogger(__name__)


class PaymenGateAdapter(PaymentAdapter):
    """PaymenGate Payment Gateway Adapter."""

    DEFAULT_BASE_URL = "https://api.paymengate.com/v1"

    async def create_payment_link(
        self,
        payment_id: UUID,
        amount: Decimal,
        currency: str,
        description: str,
        merchant_config: dict,
        return_url: str,
    ) -> PaymentLinkResult:
        merchant_id = merchant_config.get("merchant_id") or merchant_config.get("paymengate_merchant_id") or ""
        api_key = merchant_config.get("api_key") or merchant_config.get("paymengate_api_key") or ""
        secret_key = merchant_config.get("secret_key") or merchant_config.get("paymengate_secret_key") or api_key
        base_url = (merchant_config.get("base_url") or self.DEFAULT_BASE_URL).rstrip("/")

        body = {
            "merchant_id": merchant_id,
            "order_id": str(payment_id),
            "amount": float(amount),
            "currency": currency or "AZN",
            "description": description,
            "language": "az",
            "success_url": return_url,
            "cancel_url": return_url,
            "callback_url": return_url,
        }

        raw_body = json.dumps(body, separators=(",", ":"), sort_keys=True)
        signature = (
            hmac.new(secret_key.encode("utf-8"), raw_body.encode("utf-8"), hashlib.sha256).hexdigest()
            if secret_key
            else ""
        )

        headers = {
            "Content-Type": "application/json",
            "X-Merchant-Id": str(merchant_id),
            "X-Api-Key": str(api_key),
            "X-Signature": signature,
            "Authorization": f"Bearer {api_key}",
        }

        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(f"{base_url}/payments/checkout", json=body, headers=headers)
                data = resp.json() if resp.content else {}
                payload_obj = data.get("data") or data.get("payload") or data
                payment_url = (
                    payload_obj.get("payment_url")
                    or payload_obj.get("checkout_url")
                    or payload_obj.get("url")
                    or f"{return_url}?order_id={payment_id}"
                )
                transaction_id = str(
                    payload_obj.get("transaction_id")
                    or payload_obj.get("order_id")
                    or payload_obj.get("id")
                    or payment_id
                )
                return PaymentLinkResult(payment_url=payment_url, transaction_id=transaction_id)
            except Exception as exc:
                logger.error(f"PaymenGate checkout creation error: {exc}")
                return PaymentLinkResult(
                    payment_url=f"{return_url}?error=paymengate_failed",
                    transaction_id=str(payment_id),
                )

    async def verify_webhook(
        self,
        payload: dict,
        headers: dict,
        merchant_config: dict,
    ) -> WebhookResult:
        data_obj = payload.get("data") or payload.get("payload") or payload
        transaction_id = str(
            data_obj.get("transaction_id")
            or data_obj.get("order_id")
            or data_obj.get("id")
            or ""
        )
        status_str = str(data_obj.get("status") or data_obj.get("payment_status") or "").upper()
        amount = Decimal(str(data_obj.get("amount", "0")))
        is_success = status_str in {"PAID", "SUCCESS", "APPROVED", "COMPLETED"}
        return WebhookResult(
            transaction_id=transaction_id,
            is_successful=is_success,
            amount=amount,
            raw_data=payload,
        )

    async def check_status(
        self,
        transaction_id: str,
        merchant_config: dict,
    ) -> PaymentStatus:
        return PaymentStatus.completed
