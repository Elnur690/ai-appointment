from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.knowledge import KnowledgeEntry, KnowledgeEntryType, KnowledgeEntryStatus

router = APIRouter()


class KnowledgeBase(BaseModel):
    type: str = "faq"
    title: str | None = None
    content: str | None = None
    question_context: str | None = None
    answer_content: str | None = None
    branch_id: str | None = None
    tags: List[str] = []


class KnowledgeCreate(KnowledgeBase):
    pass


class KnowledgeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    question_context: str | None = None
    answer_content: str | None = None
    tags: List[str] | None = None


class KnowledgeResponse(KnowledgeBase):
    id: str
    business_id: str
    status: str


class CorrectionCreate(BaseModel):
    conversation_id: str | None = None
    question_context: str
    ai_original_response: str | None = None
    correct_answer: str
    correction_notes: str | None = None


class BestPracticeCreate(BaseModel):
    conversation_id: str | None = None
    question_context: str
    good_response: str
    notes: str | None = None


class SearchRequest(BaseModel):
    query: str


class SearchResponse(BaseModel):
    results: List[KnowledgeResponse]


_DB_ENUM_CATEGORIES = {"faq", "correction", "best_practice"}
_EXTENDED_CATEGORIES = {"policy", "service_info"}
_ALLOWED_CATEGORIES = _DB_ENUM_CATEGORIES | _EXTENDED_CATEGORIES


def _to_response(k: KnowledgeEntry) -> KnowledgeResponse:
    raw_type = k.entry_type.value if hasattr(k.entry_type, "value") else str(k.entry_type)
    stored_category = k.tags.get("category") if isinstance(k.tags, dict) else None
    display_type = stored_category if stored_category in _ALLOWED_CATEGORIES else raw_type
    return KnowledgeResponse(
        id=str(k.id),
        business_id=str(k.business_id),
        branch_id=str(k.branch_id) if k.branch_id else None,
        type=display_type,
        title=k.title,
        content=k.answer_content,
        question_context=k.question_context,
        answer_content=k.answer_content,
        status=k.status.value if hasattr(k.status, "value") else str(k.status),
        tags=list(k.tags.get("items", [])) if isinstance(k.tags, dict) else [],
    )


@router.get("/", response_model=List[KnowledgeResponse])
async def list_knowledge(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    type: str | None = None,
    status: str | None = None,
    branch_id: str | None = None,
):
    """List knowledge entries from PostgreSQL."""
    stmt = select(KnowledgeEntry).where(KnowledgeEntry.business_id == UUID(business_id))
    type_filter = type.lower() if type else None
    if type_filter:
        if type_filter in _DB_ENUM_CATEGORIES:
            stmt = stmt.where(KnowledgeEntry.entry_type == KnowledgeEntryType(type_filter))
        elif type_filter in _EXTENDED_CATEGORIES:
            stmt = stmt.where(KnowledgeEntry.tags["category"].astext == type_filter)
        else:
            return []
    if status:
        stmt = stmt.where(KnowledgeEntry.status == KnowledgeEntryStatus(status.lower()))
    if branch_id:
        stmt = stmt.where(KnowledgeEntry.branch_id == UUID(branch_id))
    stmt = stmt.order_by(KnowledgeEntry.created_at.desc())
    res = await db.execute(stmt)
    items = [_to_response(k) for k in res.scalars().all()]
    if type_filter in _DB_ENUM_CATEGORIES:
        items = [it for it in items if it.type == type_filter]
    return items


@router.post("/", response_model=KnowledgeResponse)
async def create_knowledge(
    entry: KnowledgeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create a new knowledge entry (FAQ, policy, service_info, best_practice, or correction) in PostgreSQL."""
    entry_type_val = entry.type.lower() if entry.type else "faq"
    if entry_type_val not in _ALLOWED_CATEGORIES:
        entry_type_val = "faq"
    db_entry_type = (
        KnowledgeEntryType(entry_type_val)
        if entry_type_val in _DB_ENUM_CATEGORIES
        else KnowledgeEntryType.FAQ
    )
    tags_payload: dict[str, Any] = {}
    if entry.tags:
        tags_payload["items"] = entry.tags
    if entry_type_val in _EXTENDED_CATEGORIES:
        tags_payload["category"] = entry_type_val
    q_text = (entry.question_context or entry.title or entry.content or "General Info").strip()
    a_text = (entry.answer_content or entry.content or entry.question_context or "").strip()
    row = KnowledgeEntry(
        business_id=UUID(business_id),
        branch_id=UUID(entry.branch_id) if entry.branch_id else None,
        entry_type=db_entry_type,
        status=KnowledgeEntryStatus.ACTIVE,
        title=entry.title or q_text[:80],
        question_context=q_text,
        answer_content=a_text,
        tags=tags_payload or None,
    )
    db.add(row)
    await db.flush()
    return _to_response(row)


@router.post("/correction", response_model=KnowledgeResponse)
async def capture_correction(
    correction: CorrectionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Capture a correction when human takes over and fixes AI mistake."""
    row = KnowledgeEntry(
        business_id=UUID(business_id),
        entry_type=KnowledgeEntryType.CORRECTION,
        status=KnowledgeEntryStatus.ACTIVE,
        title=f"Correction: {correction.question_context[:60]}",
        question_context=correction.question_context.strip(),
        answer_content=correction.correct_answer.strip(),
        ai_original_response=correction.ai_original_response,
        correction_notes=correction.correction_notes,
    )
    db.add(row)
    await db.flush()
    return _to_response(row)


@router.post("/best-practice", response_model=KnowledgeResponse)
async def mark_best_practice(
    bp: BestPracticeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Mark a good AI response as a best practice."""
    row = KnowledgeEntry(
        business_id=UUID(business_id),
        entry_type=KnowledgeEntryType.BEST_PRACTICE,
        status=KnowledgeEntryStatus.ACTIVE,
        title=f"Best Practice: {bp.question_context[:60]}",
        question_context=bp.question_context.strip(),
        answer_content=bp.good_response.strip(),
        correction_notes=bp.notes,
    )
    db.add(row)
    await db.flush()
    return _to_response(row)


@router.put("/{id}/approve", response_model=KnowledgeResponse)
async def approve_correction(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Approve a pending correction."""
    stmt = select(KnowledgeEntry).where(KnowledgeEntry.id == UUID(id), KnowledgeEntry.business_id == UUID(business_id))
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    row.status = KnowledgeEntryStatus.ACTIVE
    await db.flush()
    return _to_response(row)


@router.put("/{id}", response_model=KnowledgeResponse)
async def update_knowledge(
    id: str,
    update_data: KnowledgeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update a knowledge entry."""
    stmt = select(KnowledgeEntry).where(KnowledgeEntry.id == UUID(id), KnowledgeEntry.business_id == UUID(business_id))
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    if update_data.title is not None:
        row.title = update_data.title
    if update_data.question_context is not None:
        row.question_context = update_data.question_context
    if update_data.answer_content is not None:
        row.answer_content = update_data.answer_content
    await db.flush()
    return _to_response(row)


@router.delete("/{id}")
async def delete_knowledge(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Delete a knowledge entry."""
    stmt = select(KnowledgeEntry).where(KnowledgeEntry.id == UUID(id), KnowledgeEntry.business_id == UUID(business_id))
    row = (await db.execute(stmt)).scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Knowledge entry not found")
    await db.delete(row)
    await db.flush()
    return {"status": "deleted"}


@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    search: SearchRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Test RAG search with a sample query."""
    pattern = f"%{search.query.strip()}%"
    stmt = select(KnowledgeEntry).where(
        KnowledgeEntry.business_id == UUID(business_id),
        KnowledgeEntry.question_context.ilike(pattern) | KnowledgeEntry.answer_content.ilike(pattern),
    )
    res = await db.execute(stmt)
    return SearchResponse(results=[_to_response(k) for k in res.scalars().all()])
