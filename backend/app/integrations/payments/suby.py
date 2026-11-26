import hashlib
import hmac
import json
import logging
import time
from decimal import Decimal
from typing import Any
from uuid import UUID

import httpx

from app.core.config import settings
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult, WebhookResult
from app.models.payment import PaymentStatus

logger = logging.getLogger(__name__)


async def convert_azn_to_usd(amount_azn: Decimal) -> tuple[Decimal, Decimal]:
    """Convert AZN to USD using live exchange rate (fallback 1 USD = 1.70 AZN)."""
    fallback_rate = Decimal("0.588235")  # 1 / 1.70
    rate = fallback_rate
    try:
        async with httpx.AsyncClient(timeout=6.0) as client:
            resp = await client.get("https://open.er-api.com/v6/latest/AZN")
            if resp.status_code == 200:
                usd_rate = resp.json().get("rates", {}).get("USD")
                if usd_rate:
                    rate = Decimal(str(usd_rate))
    except Exception as exc:
        logger.warning(f"Live AZN->USD rate fetch failed, using fallback 1.70: {exc}")
    usd_amount = (Decimal(str(amount_azn)) * rate).quantize(Decimal("0.01"))
    if usd_amount < Decimal("0.50"):
        usd_amount = Decimal("0.50")
    return usd_amount, rate


class SubyAdapter(PaymentAdapter):
    """
    Official Suby.fi v3-beta Merchant API Adapter
    Docs: https://docs.suby.fi/v3-beta/api-reference/overview
    Base URL: https://api.beta.suby.fi/v3 (auth via `X-Suby-Api-Key`, env inferred from `sk_live_` / `sk_sandbox_`)
    """

    def _base_url(self, merchant_config: dict | None = None) -> str:
        cfg = merchant_config or {}
        return (cfg.get("api_url") or settings.SUBY_API_URL or "https://api.beta.suby.fi/v3").rstrip("/")

    def _api_key(self, merchant_config: dict | None = None) -> str:
        cfg = merchant_config or {}
        api_key = (cfg.get("api_key") or cfg.get("suby_api_key") or settings.SUBY_API_KEY or "").strip()
        if not api_key:
            raise ValueError("SUBY_API_KEY is not configured")
        return api_key

    def _headers(self, merchant_config: dict | None = None) -> dict[str, str]:
        return {
            "X-Suby-Api-Key": self._api_key(merchant_config),
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json_body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        url = f"{self._base_url(merchant_config)}/{path.lstrip('/')}"
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.request(
                method.upper(),
                url,
                headers=self._headers(merchant_config),
                json=json_body,
                params=params,
            )
            if resp.status_code >= 400:
                logger.error(f"Suby {method.upper()} {path} failed ({resp.status_code}): {resp.text}")
                raise ValueError(f"Suby API error ({resp.status_code}): {resp.text}")
            if not resp.text.strip():
                return {"status": "ok"}
            try:
                return resp.json()
            except Exception:
                return {"raw": resp.text}

    # ------------------------------------------------------------------
    # 1. CHECKOUT SESSIONS (/v3/checkout/sessions)
    # ------------------------------------------------------------------
    async def create_checkout_session(
        self,
        *,
        mode: str = "payment",  # "payment" or "subscription"
        product_id: str | None = None,
        amount: Decimal | float | None = None,
        currency: str = "USD",
        description: str | None = None,
        customer_email: str | None = None,
        customer_id: str | None = None,
        customer_name: str | None = None,
        success_url: str | None = None,
        cancel_url: str | None = None,
        expires_at: str | None = None,
        metadata: dict[str, Any] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "mode": mode,
        }
        if product_id:
            payload["productId"] = product_id
        if amount is not None and not product_id:
            payload["amount"] = float(Decimal(str(amount)).quantize(Decimal("0.01")))
            payload["currency"] = (currency or "USD").upper()
        if description:
            payload["description"] = description
        if customer_id:
            payload["customerId"] = customer_id
        elif customer_email:
            cust: dict[str, Any] = {"email": customer_email}
            if customer_name:
                cust["name"] = customer_name
            payload["customer"] = cust
        if success_url:
            payload["successUrl"] = success_url
        if cancel_url:
            payload["cancelUrl"] = cancel_url
        if expires_at:
            payload["expiresAt"] = expires_at
        if metadata:
            payload["metadata"] = metadata
        return await self._request("POST", "/checkout/sessions", json_body=payload, merchant_config=merchant_config)

    async def get_checkout_session(
        self, session_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request("GET", f"/checkout/sessions/{session_id}", merchant_config=merchant_config)

    async def list_checkout_sessions(
        self, *, limit: int = 50, offset: int = 0, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "GET", "/checkout/sessions", params={"limit": limit, "offset": offset}, merchant_config=merchant_config
        )

    async def cancel_checkout_session(
        self, session_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request("POST", f"/checkout/sessions/{session_id}/cancel", merchant_config=merchant_config)

    # ------------------------------------------------------------------
    # 2. PRODUCTS & PLANS (/v3/products)
    # ------------------------------------------------------------------
    async def create_product(
        self,
        *,
        name: str,
        price: Decimal | float,
        currency: str = "USD",
        description: str | None = None,
        recurring_interval: str | None = None,  # e.g. "month", "year", "week", "day"
        metadata: dict[str, Any] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "name": name,
            "price": float(Decimal(str(price)).quantize(Decimal("0.01"))),
            "currency": (currency or "USD").upper(),
        }
        if description:
            payload["description"] = description
        if recurring_interval:
            payload["recurringInterval"] = recurring_interval
        if metadata:
            payload["metadata"] = metadata
        return await self._request("POST", "/products", json_body=payload, merchant_config=merchant_config)

    async def get_product(self, product_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("GET", f"/products/{product_id}", merchant_config=merchant_config)

    async def list_products(
        self, *, limit: int = 50, offset: int = 0, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "GET", "/products", params={"limit": limit, "offset": offset}, merchant_config=merchant_config
        )

    async def update_product(
        self, product_id: str, updates: dict[str, Any], *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request("PATCH", f"/products/{product_id}", json_body=updates, merchant_config=merchant_config)

    async def delete_product(self, product_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("DELETE", f"/products/{product_id}", merchant_config=merchant_config)

    # ------------------------------------------------------------------
    # 3. SUBSCRIPTIONS (/v3/subscriptions)
    # ------------------------------------------------------------------
    async def get_subscription(
        self, subscription_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request("GET", f"/subscriptions/{subscription_id}", merchant_config=merchant_config)

    async def list_subscriptions(
        self,
        *,
        customer_id: str | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if customer_id:
            params["customerId"] = customer_id
        if status:
            params["status"] = status
        return await self._request("GET", "/subscriptions", params=params, merchant_config=merchant_config)

    async def update_subscription(
        self, subscription_id: str, updates: dict[str, Any], *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "PATCH", f"/subscriptions/{subscription_id}", json_body=updates, merchant_config=merchant_config
        )

    async def cancel_subscription(
        self,
        subscription_id: str,
        *,
        cancel_at_period_end: bool = False,
        reason: str | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"cancelAtPeriodEnd": cancel_at_period_end}
        if reason:
            body["reason"] = reason
        return await self._request(
            "POST", f"/subscriptions/{subscription_id}/cancel", json_body=body, merchant_config=merchant_config
        )

    async def pause_subscription(
        self, subscription_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request("POST", f"/subscriptions/{subscription_id}/pause", merchant_config=merchant_config)

    async def resume_subscription(
        self, subscription_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request("POST", f"/subscriptions/{subscription_id}/resume", merchant_config=merchant_config)

    # ------------------------------------------------------------------
    # 4. CUSTOMERS & PAYMENT METHODS (/v3/customers)
    # ------------------------------------------------------------------
    async def create_customer(
        self,
        *,
        email: str,
        name: str | None = None,
        phone: str | None = None,
        metadata: dict[str, Any] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"email": email}
        if name:
            body["name"] = name
        if phone:
            body["phone"] = phone
        if metadata:
            body["metadata"] = metadata
        return await self._request("POST", "/customers", json_body=body, merchant_config=merchant_config)

    async def get_customer(self, customer_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("GET", f"/customers/{customer_id}", merchant_config=merchant_config)

    async def list_customers(
        self, *, limit: int = 50, offset: int = 0, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "GET", "/customers", params={"limit": limit, "offset": offset}, merchant_config=merchant_config
        )

    async def update_customer(
        self, customer_id: str, updates: dict[str, Any], *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "PATCH", f"/customers/{customer_id}", json_body=updates, merchant_config=merchant_config
        )

    async def list_customer_payment_methods(
        self, customer_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "GET", f"/customers/{customer_id}/payment-methods", merchant_config=merchant_config
        )

    async def delete_customer_payment_method(
        self, customer_id: str, payment_method_id: str, *, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "DELETE",
            f"/customers/{customer_id}/payment-methods/{payment_method_id}",
            merchant_config=merchant_config,
        )

    # ------------------------------------------------------------------
    # 5. PAYMENTS & OFF-SESSION CHARGES (/v3/payments)
    # ------------------------------------------------------------------
    async def create_payment(
        self,
        *,
        amount: Decimal | float,
        currency: str = "USD",
        customer_id: str | None = None,
        customer_email: str | None = None,
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "amount": float(Decimal(str(amount)).quantize(Decimal("0.01"))),
            "currency": (currency or "USD").upper(),
        }
        if customer_id:
            body["customerId"] = customer_id
        if customer_email:
            body["customerEmail"] = customer_email
        if description:
            body["description"] = description
        if metadata:
            body["metadata"] = metadata
        return await self._request("POST", "/payments", json_body=body, merchant_config=merchant_config)

    async def create_off_session_payment(
        self,
        *,
        customer_id: str,
        payment_method_id: str,
        amount: Decimal | float,
        currency: str = "USD",
        description: str | None = None,
        metadata: dict[str, Any] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {
            "customerId": customer_id,
            "paymentMethodId": payment_method_id,
            "amount": float(Decimal(str(amount)).quantize(Decimal("0.01"))),
            "currency": (currency or "USD").upper(),
        }
        if description:
            body["description"] = description
        if metadata:
            body["metadata"] = metadata
        return await self._request("POST", "/payments/off-session", json_body=body, merchant_config=merchant_config)

    async def get_payment(self, payment_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("GET", f"/payments/{payment_id}", merchant_config=merchant_config)

    async def list_payments(
        self, *, limit: int = 50, offset: int = 0, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "GET", "/payments", params={"limit": limit, "offset": offset}, merchant_config=merchant_config
        )

    async def cancel_payment(self, payment_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("POST", f"/payments/{payment_id}/cancel", merchant_config=merchant_config)

    # ------------------------------------------------------------------
    # 6. REFUNDS (/v3/refunds)
    # ------------------------------------------------------------------
    async def create_refund(
        self,
        *,
        payment_id: str,
        amount: Decimal | float | None = None,
        reason: str | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"paymentId": payment_id}
        if amount is not None:
            body["amount"] = float(Decimal(str(amount)).quantize(Decimal("0.01")))
        if reason:
            body["reason"] = reason
        return await self._request("POST", "/refunds", json_body=body, merchant_config=merchant_config)

    async def get_refund(self, refund_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("GET", f"/refunds/{refund_id}", merchant_config=merchant_config)

    async def list_refunds(
        self, *, limit: int = 50, offset: int = 0, merchant_config: dict | None = None
    ) -> dict[str, Any]:
        return await self._request(
            "GET", "/refunds", params={"limit": limit, "offset": offset}, merchant_config=merchant_config
        )

    # ------------------------------------------------------------------
    # 7. WEBHOOKS MANAGEMENT (/v3/webhooks)
    # ------------------------------------------------------------------
    async def create_webhook(
        self,
        *,
        url: str,
        events: list[str] | None = None,
        merchant_config: dict | None = None,
    ) -> dict[str, Any]:
        body: dict[str, Any] = {"url": url}
        if events:
            body["events"] = events
        return await self._request("POST", "/webhooks", json_body=body, merchant_config=merchant_config)

    async def list_webhooks(self, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("GET", "/webhooks", merchant_config=merchant_config)

    async def delete_webhook(self, webhook_id: str, *, merchant_config: dict | None = None) -> dict[str, Any]:
        return await self._request("DELETE", f"/webhooks/{webhook_id}", merchant_config=merchant_config)

    # ------------------------------------------------------------------
    # PaymentAdapter Interface Implementation
    # ------------------------------------------------------------------
    async def create_payment_link(
        self,
        payment_id: UUID,
        amount: Decimal,
        currency: str,
        description: str,
        merchant_config: dict,
        return_url: str,
    ) -> PaymentLinkResult:
        """Create a hosted Suby.fi v3 checkout session (one-time or recurring subscription)."""
        curr = (currency or "USD").upper()
        charge_amount = Decimal(str(amount))
        if curr == "AZN":
            charge_amount, _ = await convert_azn_to_usd(charge_amount)
            curr = "USD"

        mode = merchant_config.get("mode") or ("subscription" if merchant_config.get("recurring_interval") else "payment")
        product_id = merchant_config.get("product_id")
        if not product_id and mode == "subscription":
            prod = await self.create_product(
                name=description[:100] or "Randevu.vip Subscription",
                price=charge_amount,
                currency=curr,
                description=description,
                recurring_interval=merchant_config.get("recurring_interval", "month"),
                metadata={"payment_id": str(payment_id)},
                merchant_config=merchant_config,
            )
            product_id = prod.get("id") or prod.get("productId") or (prod.get("data") or {}).get("id")

        session = await self.create_checkout_session(
            mode=mode,
            product_id=product_id,
            amount=None if product_id else charge_amount,
            currency=curr,
            description=description,
            customer_email=merchant_config.get("customer_email"),
            customer_id=merchant_config.get("customer_id"),
            customer_name=merchant_config.get("customer_name"),
            success_url=return_url,
            cancel_url=merchant_config.get("cancel_url") or return_url,
            metadata={
                "payment_id": str(payment_id),
                **(merchant_config.get("metadata") or {}),
            },
            merchant_config=merchant_config,
        )
        data = session.get("data") if isinstance(session.get("data"), dict) else session
        session_id = str(data.get("id") or data.get("sessionId") or payment_id)
        checkout_url = data.get("url") or data.get("checkoutUrl") or data.get("checkout_url")
        if not checkout_url:
            raise ValueError(f"Suby checkout session did not return a URL: {session}")

        return PaymentLinkResult(
            payment_url=checkout_url,
            transaction_id=session_id,
        )

    async def verify_webhook(
        self,
        payload: dict,
        headers: dict,
        merchant_config: dict,
        raw_body: bytes | None = None,
    ) -> WebhookResult:
        """
        Verify Suby.fi webhook using HMAC-SHA256:
          Message = "{X-Webhook-Timestamp}.{raw_body}"
          Header  = "X-Webhook-Signature" (supports both "v1=<hex>" and "<hex>")
        """
        secret = (
            (merchant_config or {}).get("webhook_secret")
            or (merchant_config or {}).get("suby_webhook_secret")
            or settings.SUBY_WEBHOOK_SECRET
            or ""
        ).strip()

        lower_headers = {str(k).lower(): str(v) for k, v in (headers or {}).items()}
        sig_header = (lower_headers.get("x-webhook-signature") or "").strip()
        ts_header = (lower_headers.get("x-webhook-timestamp") or "").strip()

        if secret:
            if not sig_header or not ts_header:
                logger.warning("Suby webhook missing X-Webhook-Signature or X-Webhook-Timestamp")
                return WebhookResult(
                    transaction_id="",
                    is_successful=False,
                    amount=Decimal("0"),
                    raw_data={"is_valid": False, "payload": payload},
                )
            try:
                event_ts = int(float(ts_header))
                if abs(int(time.time()) - event_ts) > 300:
                    logger.warning(f"Suby webhook timestamp outside 5m tolerance: {ts_header}")
                    return WebhookResult(
                        transaction_id="",
                        is_successful=False,
                        amount=Decimal("0"),
                        raw_data={"is_valid": False, "payload": payload},
                    )
            except ValueError:
                return WebhookResult(
                    transaction_id="",
                    is_successful=False,
                    amount=Decimal("0"),
                    raw_data={"is_valid": False, "payload": payload},
                )

            body_bytes = raw_body if raw_body is not None else json.dumps(payload, separators=(",", ":")).encode("utf-8")
            signed_payload = f"{ts_header}.".encode("utf-8") + body_bytes
            expected_hex = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()

            provided_sig = sig_header
            if provided_sig.startswith("v1="):
                provided_sig = provided_sig[3:]

            if not hmac.compare_digest(provided_sig.lower(), expected_hex.lower()):
                logger.warning("Suby webhook HMAC-SHA256 signature verification failed")
                return WebhookResult(
                    transaction_id="",
                    is_successful=False,
                    amount=Decimal("0"),
                    raw_data={"is_valid": False, "payload": payload},
                )

        event_type = str(payload.get("type") or payload.get("event") or payload.get("eventType") or "").upper()
        data = payload.get("data") if isinstance(payload.get("data"), dict) else payload
        meta = data.get("metadata") if isinstance(data.get("metadata"), dict) else {}

        tx_id = str(
            data.get("id")
            or data.get("paymentId")
            or data.get("sessionId")
            or data.get("subscriptionId")
            or ""
        )
        payment_id_str = meta.get("payment_id") or data.get("payment_id")
        payment_uuid = None
        if payment_id_str:
            try:
                payment_uuid = UUID(str(payment_id_str))
            except ValueError:
                payment_uuid = None

        success_events = {
            "CHECKOUT_SUCCESS",
            "PAYMENT_SUCCESS",
            "PAYMENT_SUCCEEDED",
            "PAYMENT.CAPTURED",
            "SUBSCRIPTION_ACTIVE",
            "SUBSCRIPTION_CREATED",
            "SUBSCRIPTION_RENEWED",
            "SUBSCRIPTION.PAID",
        }
        is_successful = event_type in success_events
        amount_val = data.get("amount") or data.get("price")
        amount_paid = Decimal(str(amount_val)) if amount_val is not None else Decimal("0")

        return WebhookResult(
            transaction_id=tx_id,
            is_successful=is_successful,
            amount=amount_paid,
            raw_data={
                "is_valid": True,
                "payment_id": str(payment_uuid) if payment_uuid else None,
                "currency": data.get("currency"),
                "payload": payload,
            },
        )

    async def check_status(self, transaction_id: str, merchant_config: dict) -> PaymentStatus:
        try:
            if transaction_id.startswith("cs_"):
                res = await self.get_checkout_session(transaction_id, merchant_config=merchant_config)
            else:
                res = await self.get_payment(transaction_id, merchant_config=merchant_config)
            data = res.get("data") if isinstance(res.get("data"), dict) else res
            status = str(data.get("status") or "").lower()
            if status in {"paid", "succeeded", "completed", "success", "active"}:
                return PaymentStatus.completed
            if status in {"failed", "canceled", "cancelled", "expired"}:
                return PaymentStatus.failed
            if status in {"refunded"}:
                return PaymentStatus.refunded
        except Exception as exc:
            logger.warning(f"Suby check_status failed for {transaction_id}: {exc}")
        return PaymentStatus.pending
