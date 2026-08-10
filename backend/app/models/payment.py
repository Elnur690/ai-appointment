import uuid
import enum
from typing import Any
from sqlalchemy import ForeignKey, String, Numeric, Enum, Boolean, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7

class PaymentMethod(str, enum.Enum):
    cash = "cash"
    payriff = "payriff"
    epoint = "epoint"

class PaymentStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    failed = "failed"
    refunded = "refunded"

class Payment(Base, TimestampMixin):
    __tablename__ = "payments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    appointment_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("appointments.id"), nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String, nullable=False, default="AZN")
    method: Mapped[PaymentMethod] = mapped_column(Enum(PaymentMethod), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(Enum(PaymentStatus), nullable=False, default=PaymentStatus.pending)
    recorded_by: Mapped[uuid.UUID | None] = mapped_column(nullable=True)
    gateway_transaction_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    business: Mapped["Business"] = relationship("Business", back_populates="payments")
    appointment: Mapped["Appointment"] = relationship("Appointment", back_populates="payment")


class PaymentGatewayConfig(Base, TimestampMixin):
    __tablename__ = "payment_gateway_configs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    provider: Mapped[str] = mapped_column(String, nullable=False)
    merchant_credentials: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    __table_args__ = (
        UniqueConstraint("business_id", "provider", name="uq_business_payment_provider"),
    )
