import logging
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.appointment import Appointment, AppointmentStatus
from app.models.service import Service
from app.models.staff import Staff

logger = logging.getLogger(__name__)


@dataclass
class ExecutiveGrowthReport:
    business_id: str
    business_name: str
    peak_demand_slot: str
    capacity_utilization_pct: float
    estimated_lost_revenue_cancellations: Decimal
    recommended_action: str


class BusinessAdvisorService:
    """AI Business Intelligence Growth Advisor analyzing real PostgreSQL appointment & revenue data."""

    async def generate_weekly_report(
        self,
        db: AsyncSession,
        business_id: str,
        business_name: str,
    ) -> ExecutiveGrowthReport:
        biz_uuid = UUID(str(business_id))
        since = datetime.now(timezone.utc) - timedelta(days=7)

        rows = (
            await db.execute(
                select(Appointment, Service.price)
                .outerjoin(Service, Appointment.service_id == Service.id)
                .where(
                    Appointment.business_id == biz_uuid,
                    Appointment.start_time >= since,
                )
            )
        ).all()

        staff_count = len(
            (
                await db.execute(
                    select(Staff.id).where(Staff.business_id == biz_uuid, Staff.is_active.is_(True))
                )
            ).scalars().all()
        ) or 1

        total_appts = len(rows)
        cancelled_lost = Decimal("0.00")
        hour_buckets: Counter[str] = Counter()

        for appt, svc_price in rows:
            if appt.status in (AppointmentStatus.cancelled, AppointmentStatus.no_show):
                cancelled_lost += Decimal(str(svc_price or 0))
            else:
                bucket = appt.start_time.strftime("%A %H:00")
                hour_buckets[bucket] += 1

        peak_slot = (
            f"{hour_buckets.most_common(1)[0][0]} ({hour_buckets.most_common(1)[0][1]} bookings)"
            if hour_buckets
            else "No bookings in the last 7 days"
        )
        # Approximate weekly capacity: 40 working slots per active staff member
        weekly_capacity = max(1, staff_count * 40)
        utilization = round(min(100.0, (total_appts / weekly_capacity) * 100.0), 1)

        if cancelled_lost > Decimal("0.00"):
            action = (
                f"Enable or tighten Beh (deposit) rules to recover ~{cancelled_lost:.2f} AZN/week "
                f"lost to cancellations & no-shows."
            )
        elif total_appts == 0:
            action = "Share your WhatsApp, Instagram, and public booking link to attract initial bookings."
        else:
            action = f"Peak demand is at {peak_slot}; ensure staff coverage is prioritized during this window."

        return ExecutiveGrowthReport(
            business_id=str(business_id),
            business_name=business_name,
            peak_demand_slot=peak_slot,
            capacity_utilization_pct=utilization,
            estimated_lost_revenue_cancellations=cancelled_lost.quantize(Decimal("0.01")),
            recommended_action=action,
        )
