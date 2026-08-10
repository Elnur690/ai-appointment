import enum
from uuid import UUID
from datetime import date, datetime
from sqlalchemy import String, Text, ForeignKey, Date, Enum as SAEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from app.models.base import Base, TimestampMixin, generate_uuid7

class WaitlistStatus(str, enum.Enum):
    PENDING = "pending"
    NOTIFIED = "notified"
    BOOKED = "booked"
    EXPIRED = "expired"
    CANCELLED = "cancelled"

class WaitlistEntry(Base, TimestampMixin):
    __tablename__ = "waitlist_entries"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id: Mapped[UUID] = mapped_column(ForeignKey("branches.id", ondelete="CASCADE"), nullable=False, index=True)
    customer_id: Mapped[UUID] = mapped_column(ForeignKey("customers.id", ondelete="CASCADE"), nullable=False)
    service_id: Mapped[UUID] = mapped_column(ForeignKey("services.id", ondelete="CASCADE"), nullable=False)
    staff_id: Mapped[UUID | None] = mapped_column(ForeignKey("staff.id", ondelete="SET NULL"), nullable=True)

    preferred_date: Mapped[date] = mapped_column(Date, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[WaitlistStatus] = mapped_column(SAEnum(WaitlistStatus, name="waitliststatus"), nullable=False, default=WaitlistStatus.PENDING)
    notified_at: Mapped[datetime | None] = mapped_column(nullable=True)
