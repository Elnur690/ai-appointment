import uuid
from typing import Any
from sqlalchemy import String, Numeric, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid7

class SaasOwner(Base, TimestampMixin):
    __tablename__ = "saas_owners"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Plan(Base, TimestampMixin):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_branches: Mapped[int] = mapped_column(default=1)
    max_whatsapp_numbers: Mapped[int] = mapped_column(default=1)
    ai_message_quota: Mapped[int] = mapped_column(default=1000)
    allows_branch_level_ai_tone: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_voice_messages: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_dynamic_pricing: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_winback_campaigns: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_discovery: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_online_payments: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_gcal_sync: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_apple_cal_sync: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_custom_domain: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_no_show_deposits: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_emergency_reassignment: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_omnichannel_messaging: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_growth_advisor: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_loyalty_program: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_combo_packages: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_group_bookings: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_product_upsells: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_ai_providers: Mapped[dict[str, Any] | list[str] | None] = mapped_column(JSONB, nullable=True, default=["gemini", "claude", "openai"])
    features: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

