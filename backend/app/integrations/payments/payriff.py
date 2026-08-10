import logging
from decimal import Decimal
from uuid import UUID
import httpx
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult, PaymentStatus

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
        merchant_id = merchant_config.get("merchant_id")
        secret_key = merchant_config.get("secret_key")
        
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
    ) -> WebhookResult:
        order_id = payload.get("orderId", "")
        status_str = payload.get("paymentStatus", "")
        amount = Decimal(str(payload.get("amount", "0")))
        is_success = status_str.upper() in ["APPROVED", "SUCCESS", "PAID"]
        return WebhookResult(transaction_id=order_id, is_successful=is_success, amount=amount, raw_data=payload)

    async def check_status(
        self,
        transaction_id: str,
        merchant_config: dict,
    ) -> PaymentStatus:
        return PaymentStatus.completed
