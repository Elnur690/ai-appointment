import logging
from decimal import Decimal
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.models.payment import Payment, PaymentGatewayConfig, PaymentMethod, PaymentStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.integrations.payments.payriff import PayriffAdapter
from app.integrations.payments.epoint import EpointAdapter
from app.integrations.payments.adapter import PaymentLinkResult

logger = logging.getLogger(__name__)

class PaymentService:
    """Manages cash payments and Azerbaijan online payment gateway processing."""
    
    def __init__(self, db: AsyncSession, business_id: UUID):
        self.db = db
        self.business_id = business_id
        self.payriff_adapter = PayriffAdapter()
        self.epoint_adapter = EpointAdapter()
    
    async def get_gateway_config(self, provider: str) -> PaymentGatewayConfig | None:
        stmt = select(PaymentGatewayConfig).where(
            and_(
                PaymentGatewayConfig.business_id == self.business_id,
                PaymentGatewayConfig.provider == provider.lower(),
                PaymentGatewayConfig.is_active.is_(True),
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def create_online_checkout(
        self,
        appointment_id: UUID,
        amount: Decimal,
        provider: str,  # 'payriff' or 'epoint'
        return_url: str,
    ) -> PaymentLinkResult:
        config = await self.get_gateway_config(provider)
        if not config:
            raise ValueError(f"Gateway {provider} is not configured or inactive for this business.")
        
        # Create payment record
        payment = Payment(
            business_id=self.business_id,
            appointment_id=appointment_id,
            amount=amount,
            currency="AZN",
            method=PaymentMethod(provider.lower()),
            status=PaymentStatus.pending,
        )
        self.db.add(payment)
        await self.db.flush()
        
        adapter = self.payriff_adapter if provider.lower() == "payriff" else self.epoint_adapter
        result = await adapter.create_payment_link(
            payment_id=payment.id,
            amount=amount,
            currency="AZN",
            description=f"Appointment {appointment_id} Booking",
            merchant_config=config.merchant_credentials,
            return_url=return_url,
        )
        
        payment.gateway_transaction_id = result.transaction_id
        await self.db.commit()
        return result
    
    async def handle_webhook_callback(self, provider: str, payload: dict, headers: dict) -> bool:
        config = await self.get_gateway_config(provider)
        if not config:
            logger.error(f"Cannot verify webhook: No active gateway config for {provider}")
            return False
        
        adapter = self.payriff_adapter if provider.lower() == "payriff" else self.epoint_adapter
        verify_res = await adapter.verify_webhook(payload, headers, config.merchant_credentials)
        
        if verify_res.is_successful and verify_res.transaction_id:
            stmt = select(Payment).where(
                and_(
                    Payment.business_id == self.business_id,
                    Payment.gateway_transaction_id == verify_res.transaction_id,
                )
            )
            res = await self.db.execute(stmt)
            payment = res.scalar_one_or_none()
            if payment:
                payment.status = PaymentStatus.completed
                if payment.appointment_id:
                    appt_res = await self.db.execute(
                        select(Appointment).where(Appointment.id == payment.appointment_id)
                    )
                    appt = appt_res.scalar_one_or_none()
                    if appt:
                        appt.status = AppointmentStatus.confirmed
                await self.db.commit()
                return True
        return False
