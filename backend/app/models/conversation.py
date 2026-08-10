import uuid
import enum
from datetime import datetime
from typing import Any, List
from sqlalchemy import ForeignKey, DateTime, String, Boolean, Enum, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7

class ConversationContextType(str, enum.Enum):
    customer = "customer"
    internal_group = "internal_group"

class MessageDirection(str, enum.Enum):
    inbound = "inbound"
    outbound = "outbound"

class Conversation(Base, TimestampMixin):
    __tablename__ = "conversations"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("branches.id"), nullable=False, index=True)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    context_type: Mapped[ConversationContextType] = mapped_column(Enum(ConversationContextType), nullable=False, default=ConversationContextType.customer)
    whatsapp_chat_jid: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_message_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    branch: Mapped["Branch"] = relationship("Branch", back_populates="conversations")
    customer: Mapped["Customer"] = relationship("Customer")
    messages: Mapped[List["Message"]] = relationship("Message", back_populates="conversation")

class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    conversation_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("conversations.id"), nullable=False, index=True)
    direction: Mapped[MessageDirection] = mapped_column(Enum(MessageDirection), nullable=False)
    sender_role: Mapped[str | None] = mapped_column(String, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    message_type: Mapped[str] = mapped_column(String, default="text")
    whatsapp_message_id: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    intent_detected: Mapped[str | None] = mapped_column(String, nullable=True)
    ai_tool_calls: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    conversation: Mapped["Conversation"] = relationship("Conversation", back_populates="messages")
