from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.business import Business, BusinessOwner

class BusinessRepository(BaseRepository[Business]):
    def __init__(self, session):
        super().__init__(Business, session)
        
    async def get_by_owner_email(self, email: str) -> Business | None:
        stmt = select(Business).join(BusinessOwner).where(BusinessOwner.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_active_businesses(self) -> list[Business]:
        stmt = select(Business).where(Business.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

class BusinessOwnerRepository(BaseRepository[BusinessOwner]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(BusinessOwner, session, business_id)
        
    async def get_by_email(self, email: str) -> BusinessOwner | None:
        stmt = self._scoped_query().where(BusinessOwner.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_by_business_id(self, business_id: UUID) -> list[BusinessOwner]:
        stmt = select(BusinessOwner).where(BusinessOwner.business_id == business_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
