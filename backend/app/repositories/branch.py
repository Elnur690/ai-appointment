from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.business import Branch

class BranchRepository(BaseRepository[Branch]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Branch, session, business_id)
        
    async def get_by_whatsapp_instance_id(self, instance_id: str) -> Branch | None:
        stmt = self._scoped_query().where(Branch.whatsapp_instance_id == instance_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
        
    async def get_by_business_id(self, business_id: UUID) -> list[Branch]:
        stmt = select(Branch).where(Branch.business_id == business_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_active_branches(self) -> list[Branch]:
        stmt = self._scoped_query().where(Branch.is_active == True)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
