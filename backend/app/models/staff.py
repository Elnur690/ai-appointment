import uuid
from datetime import time
from typing import List
from sqlalchemy import String, ForeignKey, Boolean, Time, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, generate_uuid7

class Staff(Base, TimestampMixin):
    __tablename__ = "staff"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    branch_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("branches.id"), nullable=False, index=True)
    business_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("businesses.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str | None] = mapped_column(String, nullable=True)
    email: Mapped[str | None] = mapped_column(String, unique=True, nullable=True)
    password_hash: Mapped[str | None] = mapped_column(String, nullable=True)
    shift_type: Mapped[str] = mapped_column(String(50), default="Full-Day (09:00 - 20:00)", nullable=False)
    allow_overtime: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    max_overtime_minutes: Mapped[int] = mapped_column(default=60, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    branch: Mapped["Branch"] = relationship("Branch", back_populates="staff")
    business: Mapped["Business"] = relationship("Business", back_populates="staff")
    schedules: Mapped[List["StaffSchedule"]] = relationship("StaffSchedule", back_populates="staff")
    staff_services: Mapped[List["StaffService"]] = relationship("StaffService", back_populates="staff")
    appointments: Mapped[List["Appointment"]] = relationship("Appointment", back_populates="staff")


class StaffSchedule(Base, TimestampMixin):
    __tablename__ = "staff_schedules"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id"), nullable=False, index=True)
    day_of_week: Mapped[int] = mapped_column(nullable=False)
    start_time: Mapped[time] = mapped_column(Time, nullable=False)
    end_time: Mapped[time] = mapped_column(Time, nullable=False)
    shift_type: Mapped[str] = mapped_column(String(50), default="full_day", nullable=False)
    allow_overtime: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    max_overtime_minutes: Mapped[int] = mapped_column(default=60, nullable=False)

    __table_args__ = (
        CheckConstraint("end_time > start_time", name="check_end_time_after_start"),
        UniqueConstraint("staff_id", "day_of_week", name="uq_staff_schedule_day"),
    )

    staff: Mapped["Staff"] = relationship("Staff", back_populates="schedules")


class StaffService(Base, TimestampMixin):
    __tablename__ = "staff_services"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    staff_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("staff.id"), nullable=False)
    service_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("services.id"), nullable=False)

    __table_args__ = (
        UniqueConstraint("staff_id", "service_id", name="uq_staff_service"),
    )

    staff: Mapped["Staff"] = relationship("Staff", back_populates="staff_services")
    service: Mapped["Service"] = relationship("Service", back_populates="staff_services")
