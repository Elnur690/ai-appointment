import uuid
from typing import Any, List
from sqlalchemy import String, Numeric, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7


class Reseller(Base, TimestampMixin):
    """Partner / Agency Reseller entity that onboards businesses onto randevu.vip and earns recurring commissions."""
    __tablename__ = "resellers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    name: Mapped[str] = mapped_column(String(150), nullable=False)
    company_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)

    referral_code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    commission_rate_percent: Mapped[float] = mapped_column(Numeric(5, 2), default=20.0, nullable=False)
    white_label_domain: Mapped[str | None] = mapped_column(String(255), unique=True, nullable=True)
    branding_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    total_earned_azn: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    total_paid_azn: Mapped[float] = mapped_column(Numeric(12, 2), default=0.0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    payouts: Mapped[List["ResellerPayout"]] = relationship("ResellerPayout", back_populates="reseller")


class ResellerPayout(Base, TimestampMixin):
    """Payout ledger entry for a reseller partner."""
    __tablename__ = "reseller_payouts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    reseller_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("resellers.id"), nullable=False, index=True)
    amount_azn: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    payment_method: Mapped[str] = mapped_column(String(50), default="bank_transfer")
    reference_note: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="completed")

    reseller: Mapped["Reseller"] = relationship("Reseller", back_populates="payouts")
