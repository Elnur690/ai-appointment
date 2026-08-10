from datetime import datetime
from uuid import UUID
from sqlalchemy import select, func
from app.repositories.base import BaseRepository
from app.models.payment import Payment

class PaymentRepository(BaseRepository[Payment]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Payment, session, business_id)
        
    async def get_by_business(self, business_id: UUID) -> list[Payment]:
        stmt = select(Payment).where(Payment.business_id == business_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_appointment(self, appointment_id: UUID) -> list[Payment]:
        stmt = self._scoped_query().where(Payment.appointment_id == appointment_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_revenue_summary(self, branch_id: UUID | None, start: datetime, end: datetime) -> float:
        stmt = select(func.sum(Payment.amount)).where(
            Payment.created_at >= start,
            Payment.created_at <= end,
            Payment.status == 'completed'
        )
        if self.business_id:
            stmt = stmt.where(Payment.business_id == self.business_id)
        if branch_id:
            stmt = stmt.where(Payment.branch_id == branch_id)
            
        result = await self.session.execute(stmt)
        total = result.scalar_one_or_none()
        return float(total) if total else 0.0
