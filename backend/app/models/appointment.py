import uuid
import enum
from datetime import datetime
from typing import List
from sqlalchemy import ForeignKey, DateTime, String, CheckConstraint, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7

class AppointmentStatus(str, enum.Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    cancelled = "cancelled"
    no_show = "no_show"

class AppointmentSource(str, enum.Enum):
    ai_chat = "ai_chat"
    staff_dashboard = "staff_dashboard"
    customer_app = "customer_app"

class Appointment(Base, TimestampMixin):
    __tablename__ = "appointments"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("branches.id"), nullable=False, index=True)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id"), nullable=False)
    customer_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("customers.id"), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"), nullable=False)
    
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, index=True)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    status: Mapped[AppointmentStatus] = mapped_column(Enum(AppointmentStatus), nullable=False, default=AppointmentStatus.pending)
    source: Mapped[AppointmentSource] = mapped_column(Enum(AppointmentSource), nullable=False, default=AppointmentSource.ai_chat)
    notes: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        CheckConstraint("end_time > start_time", name="check_appointment_end_time_after_start"),
    )

    branch: Mapped["Branch"] = relationship("Branch", back_populates="appointments")
    staff: Mapped["Staff"] = relationship("Staff", back_populates="appointments")
    customer: Mapped["Customer"] = relationship("Customer", back_populates="appointments")
    service: Mapped["Service"] = relationship("Service")
    payment: Mapped["Payment"] = relationship("Payment", back_populates="appointment")
