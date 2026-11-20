import uuid
from typing import Any
from sqlalchemy import String, Numeric, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid7

DEFAULT_PLATFORM_GATEWAYS = {
    "cash": {
        "provider": "cash",
        "name": "Cash Payment (At Venue)",
        "description": "In-person cash & POS terminal payments recorded at the salon, clinic, or studio.",
        "enabled": True,
        "requires_credentials": False,
    },
    "payriff": {
        "provider": "payriff",
        "name": "Payriff Payment Gateway",
        "description": "Online card checkout and automated no-show deposit links via Payriff API.",
        "enabled": True,
        "requires_credentials": True,
    },
    "paymegate": {
        "provider": "paymegate",
        "name": "Paymegate Payment Gateway",
        "description": "Online card & crypto checkout via official Paymegate Merchant API v1 (api.paymegate.com).",
        "enabled": True,
        "requires_credentials": True,
    },
    "creem": {
        "provider": "creem",
        "name": "Creem (Cards & Subscriptions)",
        "description": "Global online card checkout and built-in recurring subscriptions via Creem API v1 (docs.creem.io).",
        "enabled": True,
        "requires_credentials": True,
    },
}


class SaasOwner(Base, TimestampMixin):
    __tablename__ = "saas_owners"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class PlatformConfig(Base, TimestampMixin):
    __tablename__ = "platform_configs"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    config_key: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, default="global")
    payment_gateways: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=DEFAULT_PLATFORM_GATEWAYS)


class Plan(Base, TimestampMixin):
    __tablename__ = "plans"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    price: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    max_branches: Mapped[int] = mapped_column(default=1)
    max_whatsapp_numbers: Mapped[int] = mapped_column(default=1)
    ai_message_quota: Mapped[int] = mapped_column(default=1000)
    allows_free_trial: Mapped[bool] = mapped_column(Boolean, default=True)
    trial_days: Mapped[int] = mapped_column(default=14)
    trial_features: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    allows_whatsapp: Mapped[bool] = mapped_column(Boolean, default=True)
    allows_instagram: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_telegram: Mapped[bool] = mapped_column(Boolean, default=False)
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
    allows_geo_routing: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_shift_management: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_cadence_engine: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_gift_vouchers: Mapped[bool] = mapped_column(Boolean, default=False)
    allows_flash_drops: Mapped[bool] = mapped_column(Boolean, default=False)
    allowed_ai_providers: Mapped[dict[str, Any] | list[str] | None] = mapped_column(
        JSONB, nullable=True, default=["gemini", "claude", "openai"]
    )
    features: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
