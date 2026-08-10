import enum
from uuid import UUID
from datetime import datetime
from sqlalchemy import String, Text, ForeignKey, Index, Enum as SAEnum, Integer, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from app.models.base import Base, TimestampMixin, generate_uuid7

class KnowledgeEntryType(str, enum.Enum):
    CORRECTION = "correction"      # Auto-captured when human takes over from AI
    FAQ = "faq"                    # Manually added by business owner
    BEST_PRACTICE = "best_practice" # Exemplary AI conversation marked by staff

class KnowledgeEntryStatus(str, enum.Enum):
    ACTIVE = "active"
    ARCHIVED = "archived"
    PENDING_REVIEW = "pending_review"  # Corrections that need staff review

class KnowledgeEntry(Base, TimestampMixin):
    __tablename__ = "knowledge_entries"
    
    id: Mapped[UUID] = mapped_column(primary_key=True, default=generate_uuid7)
    business_id: Mapped[UUID] = mapped_column(ForeignKey("businesses.id", ondelete="CASCADE"), nullable=False, index=True)
    branch_id: Mapped[UUID | None] = mapped_column(ForeignKey("branches.id", ondelete="SET NULL"), nullable=True)
    
    entry_type: Mapped[KnowledgeEntryType] = mapped_column(SAEnum(KnowledgeEntryType, name="knowledgeentrytype"), nullable=False)
    status: Mapped[KnowledgeEntryStatus] = mapped_column(SAEnum(KnowledgeEntryStatus, name="knowledgeentrystatus"), nullable=False, default=KnowledgeEntryStatus.ACTIVE)
    
    # Content fields
    title: Mapped[str] = mapped_column(String(500), nullable=False)  # Short summary
    question_context: Mapped[str] = mapped_column(Text, nullable=False)  # What the customer asked / the situation
    answer_content: Mapped[str] = mapped_column(Text, nullable=False)    # The correct response / resolution
    
    # For corrections: link to the original conversation
    conversation_id: Mapped[UUID | None] = mapped_column(ForeignKey("conversations.id", ondelete="SET NULL"), nullable=True)
    
    # AI mistake context (for corrections)
    ai_original_response: Mapped[str | None] = mapped_column(Text, nullable=True)  # What the AI said wrong
    correction_notes: Mapped[str | None] = mapped_column(Text, nullable=True)       # Staff notes on what was wrong
    
    # Metadata
    tags: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # {"category": "pricing", "service": "haircut"}
    usage_count: Mapped[int] = mapped_column(Integer, default=0)  # How many times retrieved
    avg_relevance_score: Mapped[float] = mapped_column(Float, default=0.0)  # Running average of similarity scores when used
    
    # Vector embedding (768 dimensions for Gemini text-embedding-004)
    embedding: Mapped[list[float]] = mapped_column(Vector(768), nullable=True)  # Nullable until embedding is generated
    
    # HNSW index for fast cosine similarity search
    __table_args__ = (
        Index(
            "idx_knowledge_entries_embedding_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
