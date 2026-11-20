import uuid
import enum
from datetime import datetime
from sqlalchemy import String, ForeignKey, Boolean, Enum, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, generate_uuid7

class WhatsAppGroupScope(str, enum.Enum):
    single_branch = "single_branch"
    all_branches = "all_branches"

class WhatsAppGroup(Base, TimestampMixin):
    __tablename__ = "whatsapp_groups"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    group_jid: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    group_name: Mapped[str | None] = mapped_column(String, nullable=True)
    added_by: Mapped[str | None] = mapped_column(String, nullable=True)
    scope: Mapped[WhatsAppGroupScope] = mapped_column(Enum(WhatsAppGroupScope), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class EscalationTicket(Base, TimestampMixin):
    __tablename__ = "escalation_tickets"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    ticket_code: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    branch_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("branches.id"), nullable=True)
    conversation_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("conversations.id"), nullable=True)
    customer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("customers.id"), nullable=True)
    customer_phone: Mapped[str] = mapped_column(String, nullable=False)
    question_text: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="open")  # open, answered
    answer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    answered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
