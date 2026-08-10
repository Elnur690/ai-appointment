import logging
from datetime import date, datetime, timezone
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.models.waitlist import WaitlistEntry, WaitlistStatus
from app.models.appointment import Appointment, AppointmentStatus
from app.models.customer import Customer

logger = logging.getLogger(__name__)

class WaitlistService:
    """Manages appointment waitlists, cancellation backfill notifications, and no-show penalties."""

    def __init__(self, db: AsyncSession, business_id: UUID):
        self.db = db
        self.business_id = business_id

    async def add_to_waitlist(
        self,
        branch_id: UUID,
        customer_id: UUID,
        service_id: UUID,
        preferred_date: date,
        staff_id: UUID | None = None,
        notes: str | None = None,
    ) -> WaitlistEntry:
        entry = WaitlistEntry(
            business_id=self.business_id,
            branch_id=branch_id,
            customer_id=customer_id,
            service_id=service_id,
            staff_id=staff_id,
            preferred_date=preferred_date,
            notes=notes,
            status=WaitlistStatus.PENDING,
        )
        self.db.add(entry)
        await self.db.commit()
        await self.db.refresh(entry)
        return entry

    async def handle_appointment_cancellation(self, appointment: Appointment) -> list[WaitlistEntry]:
        """Triggered when an appointment is cancelled to find and notify waitlisted customers."""
        target_date = appointment.start_time.date()
        stmt = select(WaitlistEntry).where(
            and_(
                WaitlistEntry.business_id == self.business_id,
                WaitlistEntry.branch_id == appointment.branch_id,
                WaitlistEntry.service_id == appointment.service_id,
                WaitlistEntry.preferred_date == target_date,
                WaitlistEntry.status == WaitlistStatus.PENDING,
            )
        )
        res = await self.db.execute(stmt)
        entries = res.scalars().all()
        
        now = datetime.now(timezone.utc)
        for entry in entries:
            entry.status = WaitlistStatus.NOTIFIED
            entry.notified_at = now
            logger.info(f"Waitlist notification sent to customer {entry.customer_id} for open slot on {target_date}")
            
        await self.db.commit()
        return list(entries)

    async def check_no_show_penalty(self, customer_id: UUID) -> bool:
        """Returns True if customer has 2+ recent no-shows and requires deposit/staff approval."""
        stmt = select(func.count(Appointment.id)).where(
            and_(
                Appointment.business_id == self.business_id,
                Appointment.customer_id == customer_id,
                Appointment.status == AppointmentStatus.no_show,
            )
        )
        res = await self.db.execute(stmt)
        count = res.scalar() or 0
        return count >= 2
