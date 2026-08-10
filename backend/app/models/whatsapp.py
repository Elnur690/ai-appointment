import uuid
import enum
from sqlalchemy import String, ForeignKey, Boolean, Enum
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
