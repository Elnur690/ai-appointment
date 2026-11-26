import hashlib
import hmac
import json
import logging
from decimal import Decimal
from uuid import UUID
import httpx
from app.core.config import settings
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult
from app.models.payment import PaymentStatus

logger = logging.getLogger(__name__)

class PayriffAdapter(PaymentAdapter):
    """Payriff Payment Gateway Adapter for Azerbaijan."""
    
    BASE_URL = "https://api.payriff.com/api/v2"
    
    async def create_payment_link(
        self,
        payment_id: UUID,
        amount: Decimal,
        currency: str,
        description: str,
        merchant_config: dict,
        return_url: str,
    ) -> PaymentLinkResult:
        merchant_id = (merchant_config.get("merchant_id") or settings.PAYRIFF_MERCHANT_ID or "").strip()
        secret_key = (merchant_config.get("secret_key") or settings.PAYRIFF_SECRET_KEY or "").strip()
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            payload = {
                "body": {
                    "amount": float(amount),
                    "currencyType": currency,
                    "description": description,
                    "language": "AZ",
                    "approveURL": return_url,
                    "cancelURL": return_url,
                    "declineURL": return_url,
                },
                "merchant": merchant_id,
            }
            headers = {"Authorization": secret_key, "Content-Type": "application/json"}
            try:
                resp = await client.post(f"{self.BASE_URL}/orders", json=payload, headers=headers)
                data = resp.json()
                order_id = data.get("payload", {}).get("orderId", str(payment_id))
                payment_url = data.get("payload", {}).get("paymentUrl", f"{return_url}?orderId={order_id}")
                return PaymentLinkResult(payment_url=payment_url, transaction_id=order_id)
            except Exception as e:
                logger.error(f"Payriff order creation error: {e}")
                return PaymentLinkResult(payment_url=f"{return_url}?error=payriff_failed", transaction_id=str(payment_id))

    async def verify_webhook(
        self,
        payload: dict,
        headers: dict,
        merchant_config: dict,
        raw_body: bytes | None = None,
    ) -> WebhookResult:
        secret_key = (
            (merchant_config or {}).get("webhook_secret")
            or (merchant_config or {}).get("secret_key")
            or settings.PAYRIFF_SECRET_KEY
            or ""
        ).strip()
        if secret_key:
            lower_headers = {str(k).lower(): str(v).strip() for k, v in (headers or {}).items()}
            provided_sig = (
                lower_headers.get("x-payriff-signature")
                or lower_headers.get("x-signature")
                or lower_headers.get("authorization")
                or str(payload.get("signature") or "").strip()
            )
            if not provided_sig:
                logger.warning("Payriff webhook missing signature/secret header")
                return WebhookResult(transaction_id="", is_successful=False, amount=Decimal("0"), raw_data=payload)

            body_bytes = raw_body if raw_body is not None else json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
            expected_hmac = hmac.new(secret_key.encode("utf-8"), body_bytes, hashlib.sha256).hexdigest()
            is_valid_sig = (
                hmac.compare_digest(provided_sig.lower(), expected_hmac.lower())
                or hmac.compare_digest(provided_sig, secret_key)
            )
            if not is_valid_sig:
                logger.warning("Payriff webhook signature verification failed")
                return WebhookResult(transaction_id="", is_successful=False, amount=Decimal("0"), raw_data=payload)

        order_id = str(payload.get("orderId", ""))
        status_str = str(payload.get("paymentStatus", ""))
        amount = Decimal(str(payload.get("amount", "0")))
        is_success = status_str.upper() in ["APPROVED", "SUCCESS", "PAID"]
        return WebhookResult(transaction_id=order_id, is_successful=is_success, amount=amount, raw_data=payload)

    async def check_status(
        self,
        transaction_id: str,
        merchant_config: dict,
    ) -> PaymentStatus:
        return PaymentStatus.completed
