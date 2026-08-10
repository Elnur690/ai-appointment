import uuid
from typing import Any, List
from sqlalchemy import String, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7

DEFAULT_AI_TONE = {
    "language": "az",
    "tone": "professional",
    "greeting_style": "formal",
    "business_description": "",
    "custom_instructions": ""
}

DEFAULT_WORKING_HOURS = {
    "monday": {"start": "09:00", "end": "18:00"},
    "tuesday": {"start": "09:00", "end": "18:00"},
    "wednesday": {"start": "09:00", "end": "18:00"},
    "thursday": {"start": "09:00", "end": "18:00"},
    "friday": {"start": "09:00", "end": "18:00"},
    "saturday": {"start": "10:00", "end": "15:00"},
    "sunday": None
}

class Business(Base, TimestampMixin):
    __tablename__ = "businesses"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    name: Mapped[str] = mapped_column(String, nullable=False)
    plan_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("plans.id"), nullable=True)
    subscription_status: Mapped[str] = mapped_column(String, default="trial")
    default_ai_tone_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True, default=DEFAULT_AI_TONE)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # AI Provider & Discovery fields
    selected_ai_provider: Mapped[str] = mapped_column(String(50), default="gemini")
    is_discoverable: Mapped[bool] = mapped_column(Boolean, default=False)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    
    owners: Mapped[List["BusinessOwner"]] = relationship("BusinessOwner", back_populates="business")
    branches: Mapped[List["Branch"]] = relationship("Branch", back_populates="business")
    staff: Mapped[List["Staff"]] = relationship("Staff", back_populates="business")
    services: Mapped[List["Service"]] = relationship("Service", back_populates="business")
    customers: Mapped[List["Customer"]] = relationship("Customer", back_populates="business")
    subscriptions: Mapped[List["Subscription"]] = relationship("Subscription", back_populates="business")
    payments: Mapped[List["Payment"]] = relationship("Payment", back_populates="business")


class BusinessOwner(Base, TimestampMixin):
    __tablename__ = "business_owners"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship("Business", back_populates="owners")


class Branch(Base, TimestampMixin):
    __tablename__ = "branches"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    whatsapp_instance_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    latitude: Mapped[float | None] = mapped_column(nullable=True)
    longitude: Mapped[float | None] = mapped_column(nullable=True)
    working_hours: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False, default=DEFAULT_WORKING_HOURS)
    timezone: Mapped[str] = mapped_column(String, nullable=False, default="Asia/Baku")
    ai_tone_config: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    business: Mapped["Business"] = relationship("Business", back_populates="branches")
    staff: Mapped[List["Staff"]] = relationship("Staff", back_populates="branch")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="branch")
    conversations: Mapped[List["Conversation"]] = relationship("Conversation", back_populates="branch")
