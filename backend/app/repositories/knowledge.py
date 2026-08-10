import logging
from uuid import UUID
from sqlalchemy import select, and_, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeEntry, KnowledgeEntryType, KnowledgeEntryStatus

logger = logging.getLogger(__name__)

class KnowledgeRepository:
    def __init__(self, session: AsyncSession, business_id: UUID):
        self.session = session
        self.business_id = business_id
    
    async def create(self, entry: KnowledgeEntry) -> KnowledgeEntry:
        entry.business_id = self.business_id
        self.session.add(entry)
        await self.session.flush()
        return entry
    
    async def get_by_id(self, entry_id: UUID) -> KnowledgeEntry | None:
        stmt = select(KnowledgeEntry).where(
            and_(
                KnowledgeEntry.id == entry_id,
                KnowledgeEntry.business_id == self.business_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def list_entries(
        self,
        entry_type: KnowledgeEntryType | None = None,
        status: KnowledgeEntryStatus | None = None,
        branch_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[KnowledgeEntry]:
        stmt = select(KnowledgeEntry).where(KnowledgeEntry.business_id == self.business_id)
        if entry_type:
            stmt = stmt.where(KnowledgeEntry.entry_type == entry_type)
        if status:
            stmt = stmt.where(KnowledgeEntry.status == status)
        if branch_id:
            stmt = stmt.where(
                (KnowledgeEntry.branch_id == branch_id) | (KnowledgeEntry.branch_id.is_(None))
            )
        stmt = stmt.order_by(KnowledgeEntry.created_at.desc()).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def search_similar(
        self,
        query_embedding: list[float],
        branch_id: UUID | None = None,
        limit: int = 5,
        similarity_threshold: float = 0.65,
        entry_types: list[KnowledgeEntryType] | None = None,
    ) -> list[tuple[KnowledgeEntry, float]]:
        """Search for similar knowledge entries using cosine similarity.
        
        Returns list of (entry, similarity_score) tuples sorted by relevance.
        """
        cosine_dist = KnowledgeEntry.embedding.cosine_distance(query_embedding)
        similarity = (1 - cosine_dist).label("similarity")
        
        filters = [
            KnowledgeEntry.business_id == self.business_id,
            KnowledgeEntry.status == KnowledgeEntryStatus.ACTIVE,
            KnowledgeEntry.embedding.isnot(None),
            (1 - cosine_dist) >= similarity_threshold,
        ]
        
        if branch_id:
            filters.append(
                (KnowledgeEntry.branch_id == branch_id) | (KnowledgeEntry.branch_id.is_(None))
            )
        
        if entry_types:
            filters.append(KnowledgeEntry.entry_type.in_(entry_types))
        
        stmt = (
            select(KnowledgeEntry, similarity)
            .where(and_(*filters))
            .order_by(cosine_dist.asc())
            .limit(limit)
        )
        
        result = await self.session.execute(stmt)
        return [(row.KnowledgeEntry, float(row.similarity)) for row in result.all()]
    
    async def update_entry(self, entry_id: UUID, **kwargs) -> KnowledgeEntry | None:
        entry = await self.get_by_id(entry_id)
        if not entry:
            return None
        for key, value in kwargs.items():
            setattr(entry, key, value)
        await self.session.flush()
        return entry
    
    async def increment_usage(self, entry_id: UUID, relevance_score: float) -> None:
        """Increment usage count and update running average relevance score."""
        entry = await self.get_by_id(entry_id)
        if entry:
            new_count = entry.usage_count + 1
            # Running average
            new_avg = ((entry.avg_relevance_score * entry.usage_count) + relevance_score) / new_count
            entry.usage_count = new_count
            entry.avg_relevance_score = new_avg
            await self.session.flush()
    
    async def delete(self, entry_id: UUID) -> bool:
        entry = await self.get_by_id(entry_id)
        if not entry:
            return False
        await self.session.delete(entry)
        await self.session.flush()
        return True
