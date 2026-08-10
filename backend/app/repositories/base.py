from typing import Generic, TypeVar, Type, Any
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    """Base repository with automatic business_id tenant scoping."""
    
    def __init__(self, model: Type[ModelType], session: AsyncSession, business_id: UUID | None = None):
        self.model = model
        self.session = session
        self.business_id = business_id
    
    def _scoped_query(self, stmt=None):
        """Apply business_id filter if the model has business_id and we have one."""
        if stmt is None:
            stmt = select(self.model)
        if self.business_id and hasattr(self.model, 'business_id'):
            stmt = stmt.where(self.model.business_id == self.business_id)
        return stmt
    
    async def get_by_id(self, id: UUID) -> ModelType | None:
        stmt = self._scoped_query().where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        stmt = self._scoped_query().offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def count(self) -> int:
        stmt = self._scoped_query(select(func.count(self.model.id)))
        result = await self.session.execute(stmt)
        return result.scalar_one()
    
    async def create(self, obj: ModelType) -> ModelType:
        if self.business_id and hasattr(obj, 'business_id') and not obj.business_id:
            obj.business_id = self.business_id
        self.session.add(obj)
        await self.session.flush()
        return obj
    
    async def update(self, obj: ModelType) -> ModelType:
        await self.session.flush()
        return obj
    
    async def delete(self, id: UUID) -> bool:
        obj = await self.get_by_id(id)
        if obj:
            await self.session.delete(obj)
            await self.session.flush()
            return True
        return False
