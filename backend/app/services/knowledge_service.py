import logging
from uuid import UUID
from dataclasses import dataclass
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.knowledge import KnowledgeEntry, KnowledgeEntryType, KnowledgeEntryStatus
from app.repositories.knowledge import KnowledgeRepository
from app.integrations.ai.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

@dataclass
class RetrievedKnowledge:
    """Knowledge entries retrieved for RAG injection into system prompt."""
    corrections: list[tuple[KnowledgeEntry, float]]  # (entry, similarity)
    faqs: list[tuple[KnowledgeEntry, float]]
    best_practices: list[tuple[KnowledgeEntry, float]]
    
    def format_for_prompt(self) -> str:
        """Format retrieved knowledge as context for the AI system prompt."""
        sections = []
        
        if self.corrections:
            lines = ["<past_corrections>"]
            for entry, score in self.corrections[:3]:  # Max 3 corrections
                lines.append(f'<correction relevance="{score:.2f}">')
                lines.append(f"  Situation: {entry.question_context}")
                if entry.ai_original_response:
                    lines.append(f"  Wrong response: {entry.ai_original_response}")
                lines.append(f"  Correct response: {entry.answer_content}")
                if entry.correction_notes:
                    lines.append(f"  Note: {entry.correction_notes}")
                lines.append("</correction>")
            lines.append("</past_corrections>")
            sections.append("\n".join(lines))
        
        if self.faqs:
            lines = ["<faq_knowledge>"]
            for entry, score in self.faqs[:3]:
                lines.append(f'<faq relevance="{score:.2f}">')
                lines.append(f"  Q: {entry.question_context}")
                lines.append(f"  A: {entry.answer_content}")
                lines.append("</faq>")
            lines.append("</faq_knowledge>")
            sections.append("\n".join(lines))
        
        if self.best_practices:
            lines = ["<best_practices>"]
            for entry, score in self.best_practices[:2]:
                lines.append(f'<example relevance="{score:.2f}">')
                lines.append(f"  Situation: {entry.question_context}")
                lines.append(f"  Good response: {entry.answer_content}")
                lines.append("</example>")
            lines.append("</best_practices>")
            sections.append("\n".join(lines))
        
        if not sections:
            return ""
        
        return (
            "\n\n--- LEARNED KNOWLEDGE (use this to improve your responses) ---\n\n"
            + "\n\n".join(sections)
            + "\n\n--- END LEARNED KNOWLEDGE ---"
        )


class KnowledgeService:
    def __init__(self, db: AsyncSession, business_id: UUID, embedding_service: EmbeddingService):
        self.db = db
        self.business_id = business_id
        self.embedding_service = embedding_service
        self.repo = KnowledgeRepository(db, business_id)
    
    async def add_faq(
        self,
        question: str,
        answer: str,
        title: str | None = None,
        branch_id: UUID | None = None,
        tags: dict | None = None,
    ) -> KnowledgeEntry:
        """Add a FAQ knowledge entry (manually by business owner)."""
        embed_text = self.embedding_service.prepare_faq_text(question, answer)
        embedding = await self.embedding_service.generate_embedding(embed_text)
        
        entry = KnowledgeEntry(
            business_id=self.business_id,
            branch_id=branch_id,
            entry_type=KnowledgeEntryType.FAQ,
            status=KnowledgeEntryStatus.ACTIVE,
            title=title or question[:100],
            question_context=question,
            answer_content=answer,
            tags=tags,
            embedding=embedding,
        )
        return await self.repo.create(entry)
    
    async def capture_correction(
        self,
        conversation_id: UUID,
        customer_question: str,
        ai_wrong_response: str,
        staff_correct_response: str,
        correction_notes: str | None = None,
        branch_id: UUID | None = None,
    ) -> KnowledgeEntry:
        """Capture a correction when human takes over from AI.
        
        Called when:
        1. AI gives wrong answer and staff corrects it
        2. Staff takes over and resolves differently than AI would have
        """
        embed_text = self.embedding_service.prepare_correction_text(
            question=customer_question,
            correct_answer=staff_correct_response,
            ai_mistake=ai_wrong_response,
        )
        embedding = await self.embedding_service.generate_embedding(embed_text)
        
        entry = KnowledgeEntry(
            business_id=self.business_id,
            branch_id=branch_id,
            entry_type=KnowledgeEntryType.CORRECTION,
            status=KnowledgeEntryStatus.PENDING_REVIEW,  # Staff should review before activating
            title=f"Correction: {customer_question[:80]}",
            question_context=customer_question,
            answer_content=staff_correct_response,
            ai_original_response=ai_wrong_response,
            correction_notes=correction_notes,
            conversation_id=conversation_id,
            tags=None,
            embedding=embedding,
        )
        return await self.repo.create(entry)
    
    async def mark_best_practice(
        self,
        conversation_id: UUID,
        customer_question: str,
        ai_good_response: str,
        branch_id: UUID | None = None,
        notes: str | None = None,
    ) -> KnowledgeEntry:
        """Mark a good AI conversation as a best practice example."""
        embed_text = self.embedding_service.prepare_faq_text(customer_question, ai_good_response)
        embedding = await self.embedding_service.generate_embedding(embed_text)
        
        entry = KnowledgeEntry(
            business_id=self.business_id,
            branch_id=branch_id,
            entry_type=KnowledgeEntryType.BEST_PRACTICE,
            status=KnowledgeEntryStatus.ACTIVE,
            title=f"Best practice: {customer_question[:80]}",
            question_context=customer_question,
            answer_content=ai_good_response,
            correction_notes=notes,
            conversation_id=conversation_id,
            embedding=embedding,
        )
        return await self.repo.create(entry)
    
    async def retrieve_relevant_knowledge(
        self,
        customer_message: str,
        branch_id: UUID | None = None,
        max_results: int = 5,
        similarity_threshold: float = 0.60,
    ) -> RetrievedKnowledge:
        """Retrieve relevant knowledge for a customer message.
        
        This is the core RAG retrieval step, called before every AI response.
        Returns categorized knowledge entries sorted by relevance.
        """
        query_text = self.embedding_service.prepare_query_text(customer_message)
        query_embedding = await self.embedding_service.generate_embedding(
            query_text, task_type="RETRIEVAL_QUERY"
        )
        
        results = await self.repo.search_similar(
            query_embedding=query_embedding,
            branch_id=branch_id,
            limit=max_results,
            similarity_threshold=similarity_threshold,
        )
        
        # Update usage counts asynchronously (fire and forget is fine)
        for entry, score in results:
            await self.repo.increment_usage(entry.id, score)
        
        # Categorize results
        corrections = [(e, s) for e, s in results if e.entry_type == KnowledgeEntryType.CORRECTION]
        faqs = [(e, s) for e, s in results if e.entry_type == KnowledgeEntryType.FAQ]
        best_practices = [(e, s) for e, s in results if e.entry_type == KnowledgeEntryType.BEST_PRACTICE]
        
        return RetrievedKnowledge(
            corrections=corrections,
            faqs=faqs,
            best_practices=best_practices,
        )
    
    async def approve_correction(self, entry_id: UUID) -> KnowledgeEntry | None:
        """Approve a pending correction (staff review)."""
        return await self.repo.update_entry(
            entry_id, status=KnowledgeEntryStatus.ACTIVE
        )
    
    async def archive_entry(self, entry_id: UUID) -> KnowledgeEntry | None:
        """Archive a knowledge entry."""
        return await self.repo.update_entry(
            entry_id, status=KnowledgeEntryStatus.ARCHIVED
        )
    
    async def update_entry(
        self,
        entry_id: UUID,
        question_context: str | None = None,
        answer_content: str | None = None,
        title: str | None = None,
        tags: dict | None = None,
    ) -> KnowledgeEntry | None:
        """Update a knowledge entry and regenerate its embedding."""
        entry = await self.repo.get_by_id(entry_id)
        if not entry:
            return None
        
        if question_context:
            entry.question_context = question_context
        if answer_content:
            entry.answer_content = answer_content
        if title:
            entry.title = title
        if tags is not None:
            entry.tags = tags
        
        # Regenerate embedding with updated content
        if question_context or answer_content:
            if entry.entry_type == KnowledgeEntryType.CORRECTION:
                embed_text = self.embedding_service.prepare_correction_text(
                    entry.question_context, entry.answer_content, entry.ai_original_response
                )
            else:
                embed_text = self.embedding_service.prepare_faq_text(
                    entry.question_context, entry.answer_content
                )
            entry.embedding = await self.embedding_service.generate_embedding(embed_text)
        
        await self.db.flush()
        return entry
    
    async def list_entries(
        self,
        entry_type: KnowledgeEntryType | None = None,
        status: KnowledgeEntryStatus | None = None,
        branch_id: UUID | None = None,
        skip: int = 0,
        limit: int = 50,
    ) -> list[KnowledgeEntry]:
        return await self.repo.list_entries(entry_type, status, branch_id, skip, limit)
    
    async def delete_entry(self, entry_id: UUID) -> bool:
        return await self.repo.delete(entry_id)
