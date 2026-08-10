import base64
import hashlib
import json
import logging
from decimal import Decimal
from uuid import UUID
import httpx
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult, PaymentStatus

logger = logging.getLogger(__name__)

class EpointAdapter(PaymentAdapter):
    """EPoint Payment Gateway Adapter for Azerbaijan."""
    
    BASE_URL = "https://epoint.az/api/1.0"
    
    async def create_payment_link(
        self,
        payment_id: UUID,
        amount: Decimal,
        currency: str,
        description: str,
        merchant_config: dict,
        return_url: str,
    ) -> PaymentLinkResult:
        public_key = merchant_config.get("public_key")
        private_key = merchant_config.get("private_key")
        
        json_data = {
            "public_key": public_key,
            "amount": float(amount),
            "currency": currency,
            "language": "az",
            "order_id": str(payment_id),
            "description": description,
            "success_redirect_url": return_url,
            "error_redirect_url": return_url,
        }
        
        data_b64 = base64.b64encode(json.dumps(json_data).encode("utf-8")).decode("utf-8")
        sign_str = private_key + data_b64 + private_key
        signature = base64.b64encode(hashlib.sha1(sign_str.encode("utf-8")).digest()).decode("utf-8")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            try:
                resp = await client.post(
                    f"{self.BASE_URL}/request",
                    data={"data": data_b64, "signature": signature},
                )
                res_json = resp.json()
                redirect_url = res_json.get("url", f"{return_url}?order_id={payment_id}")
                transaction_id = res_json.get("transaction", str(payment_id))
                return PaymentLinkResult(payment_url=redirect_url, transaction_id=transaction_id)
            except Exception as e:
                logger.error(f"EPoint order creation error: {e}")
                return PaymentLinkResult(payment_url=f"{return_url}?error=epoint_failed", transaction_id=str(payment_id))

    async def verify_webhook(
        self,
        payload: dict,
        headers: dict,
        merchant_config: dict,
    ) -> WebhookResult:
        data_b64 = payload.get("data", "")
        try:
            raw_bytes = base64.b64decode(data_b64)
            decoded = json.loads(raw_bytes.decode("utf-8"))
            order_id = decoded.get("order_id", "")
            status_str = decoded.get("status", "")
            amount = Decimal(str(decoded.get("amount", "0")))
            is_success = status_str.lower() in ["success", "approved"]
            return WebhookResult(transaction_id=order_id, is_successful=is_success, amount=amount, raw_data=decoded)
        except Exception as e:
            logger.error(f"EPoint webhook parsing error: {e}")
            return WebhookResult(transaction_id="", is_successful=False, amount=Decimal("0"), raw_data=payload)

    async def check_status(
        self,
        transaction_id: str,
        merchant_config: dict,
    ) -> PaymentStatus:
        return PaymentStatus.completed
