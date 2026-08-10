from uuid import UUID
from datetime import datetime
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.subscription import Subscription

class SubscriptionRepository(BaseRepository[Subscription]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Subscription, session, business_id)
        
    async def get_active_by_business(self, business_id: UUID) -> list[Subscription]:
        stmt = select(Subscription).where(
            Subscription.business_id == business_id,
            Subscription.status == 'active'
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_current(self, business_id: UUID) -> Subscription | None:
        now = datetime.utcnow()
        stmt = select(Subscription).where(
            Subscription.business_id == business_id,
            Subscription.status == 'active',
            Subscription.current_period_start <= now,
            Subscription.current_period_end >= now
        ).order_by(Subscription.created_at.desc())
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
