import logging
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.config import settings
from app.core.security import decrypt_credentials_dict
from app.models.payment import Payment, PaymentGatewayConfig, PaymentMethod, PaymentStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.integrations.payments.payriff import PayriffAdapter
from app.integrations.payments.epoint import EpointAdapter
from app.integrations.payments.suby import SubyAdapter
# Disabled providers (kept commented for reference):
# from app.integrations.payments.paymegate import PaymegateAdapter
# from app.integrations.payments.creem import CreemAdapter
from app.integrations.payments.adapter import PaymentAdapter, PaymentLinkResult

logger = logging.getLogger(__name__)


class PaymentService:
    """Manages cash payments and online payment gateway processing (Suby.fi, Payriff & EPoint)."""

    def __init__(self, db: AsyncSession, business_id: UUID):
        self.db = db
        self.business_id = business_id
        self.payriff_adapter = PayriffAdapter()
        self.epoint_adapter = EpointAdapter()
        self.suby_adapter = SubyAdapter()
        # self.paymegate_adapter = PaymegateAdapter()
        # self.creem_adapter = CreemAdapter()

    def _get_adapter(self, provider: str) -> PaymentAdapter:
        norm = provider.lower().strip()
        if norm == "suby":
            return self.suby_adapter
        if norm == "payriff":
            return self.payriff_adapter
        # if norm == "creem":
        #     return self.creem_adapter
        # if norm in {"paymegate", "paymengate"}:
        #     return self.paymegate_adapter
        return self.epoint_adapter

    async def get_gateway_config(self, provider: str) -> PaymentGatewayConfig | None:
        norm = provider.lower().strip()
        stmt = select(PaymentGatewayConfig).where(
            and_(
                PaymentGatewayConfig.business_id == self.business_id,
                PaymentGatewayConfig.provider == norm,
                PaymentGatewayConfig.is_active.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def create_online_checkout(
        self,
        appointment_id: UUID | None,
        amount: Decimal,
        provider: str,  # 'suby', 'payriff', or 'epoint'
        return_url: str,
        description: str | None = None,
        extra_metadata: dict | None = None,
    ) -> PaymentLinkResult:
        config = await self.get_gateway_config(provider)
        norm = provider.lower().strip()
        merchant_creds = decrypt_credentials_dict(config.merchant_credentials) if config else {}
        if norm == "suby" and not merchant_creds.get("api_key") and not settings.SUBY_API_KEY:
            raise ValueError("Suby API key is not configured.")
        # if norm == "creem" and not merchant_creds.get("api_key") and not settings.CREEM_API_KEY:
        #     raise ValueError("Creem API key is not configured.")
        # if norm == "paymegate" and not merchant_creds.get("api_key") and not settings.PAYMEGATE_API_KEY:
        #     raise ValueError("Paymegate API key is not configured.")
        if norm == "payriff" and not merchant_creds.get("secret_key") and not settings.PAYRIFF_SECRET_KEY:
            raise ValueError("Payriff credentials are not configured.")

        payment = Payment(
            business_id=self.business_id,
            appointment_id=appointment_id,
            amount=amount,
            currency="AZN",
            method=PaymentMethod(norm if norm in {"suby", "payriff", "epoint"} else "suby"),
            status=PaymentStatus.pending,
            notes=description,
        )
        self.db.add(payment)
        await self.db.flush()

        merchant_creds["business_id"] = str(self.business_id)
        if extra_metadata:
            merchant_creds.update(extra_metadata)

        adapter = self._get_adapter(norm)
        result = await adapter.create_payment_link(
            payment_id=payment.id,
            amount=amount,
            currency="AZN",
            description=description or (f"Appointment {appointment_id} Booking" if appointment_id else "Randevu.vip Payment"),
            merchant_config=merchant_creds,
            return_url=return_url,
        )

        payment.gateway_transaction_id = result.transaction_id
        await self.db.commit()
        return result

    async def handle_webhook_callback(self, provider: str, payload: dict, headers: dict) -> bool:
        config = await self.get_gateway_config(provider)
        merchant_creds = decrypt_credentials_dict(config.merchant_credentials) if config else {}

        adapter = self._get_adapter(provider)
        verify_res = await adapter.verify_webhook(payload, headers, merchant_creds)

        if verify_res.is_successful and verify_res.transaction_id:
            stmt = select(Payment).where(
                and_(
                    Payment.business_id == self.business_id,
                    Payment.gateway_transaction_id == verify_res.transaction_id,
                )
            )
            payment = (await self.db.execute(stmt)).scalar_one_or_none()

            if not payment:
                ext_id = payload.get("externalId") or (payload.get("metadata") or {}).get("paymentId")
                if ext_id:
                    try:
                        payment = (
                            await self.db.execute(
                                select(Payment).where(
                                    Payment.business_id == self.business_id,
                                    Payment.id == UUID(str(ext_id)),
                                )
                            )
                        ).scalar_one_or_none()
                    except ValueError:
                        payment = None

            if payment:
                payment.status = PaymentStatus.completed
                if payment.appointment_id:
                    appt = (
                        await self.db.execute(
                            select(Appointment).where(Appointment.id == payment.appointment_id)
                        )
                    ).scalar_one_or_none()
                    if appt:
                        appt.status = AppointmentStatus.confirmed
                await self.db.commit()
                return True
        return False
