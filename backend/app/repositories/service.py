from uuid import UUID
from sqlalchemy import select
from app.repositories.base import BaseRepository
from app.models.service import Service

class ServiceRepository(BaseRepository[Service]):
    def __init__(self, session, business_id: UUID | None = None):
        super().__init__(Service, session, business_id)
        
    async def get_by_branch_id(self, branch_id: UUID) -> list[Service]:
        stmt = self._scoped_query().where(Service.branch_id == branch_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_active_services(self, branch_id: UUID | None = None) -> list[Service]:
        stmt = self._scoped_query().where(Service.is_active == True)
        if branch_id:
            stmt = stmt.where(Service.branch_id == branch_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
        
    async def get_by_business_id(self, business_id: UUID) -> list[Service]:
        stmt = select(Service).where(Service.business_id == business_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
