import uuid
from typing import List
from sqlalchemy import String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7

class Customer(Base, TimestampMixin):
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    name: Mapped[str | None] = mapped_column(String, nullable=True)
    language_pref: Mapped[str] = mapped_column(String(10), nullable=False, default="az")

    __table_args__ = (
        UniqueConstraint("business_id", "phone_number", name="uq_business_customer_phone"),
    )

    business: Mapped["Business"] = relationship("Business", back_populates="customers")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="customer")
