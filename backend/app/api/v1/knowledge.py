from typing import Annotated, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class KnowledgeBaseModel(BaseModel):
    title: str
    content: str
    type: str  # faq, best_practice
    branch_id: str | None = None

class KnowledgeCreate(KnowledgeBaseModel):
    pass

class KnowledgeUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None

class KnowledgeResponse(KnowledgeBaseModel):
    id: str
    business_id: str
    status: str

class CorrectionCreate(BaseModel):
    conversation_id: str
    correction_text: str

class SearchRequest(BaseModel):
    query: str

class SearchResponse(BaseModel):
    results: List[KnowledgeResponse]

@router.get("/", response_model=List[KnowledgeResponse])
async def list_knowledge(
    type: str | None = None,
    status: str | None = None,
    branch_id: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List knowledge entries."""
    return []

@router.post("/", response_model=KnowledgeResponse)
async def create_knowledge(
    entry: KnowledgeCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Create a new knowledge entry (FAQ or best practice)."""
    return KnowledgeResponse(
        id="temp", business_id=business_id, status="active", **entry.model_dump()
    )

@router.get("/{id}", response_model=KnowledgeResponse)
async def get_knowledge(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get a knowledge entry by ID."""
    return KnowledgeResponse(
        id=id, business_id=business_id, title="Example", content="content",
        type="faq", status="active"
    )

@router.put("/{id}", response_model=KnowledgeResponse)
async def update_knowledge(
    id: str,
    update_data: KnowledgeUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Update a knowledge entry."""
    return KnowledgeResponse(
        id=id, business_id=business_id, title=update_data.title or "Example",
        content=update_data.content or "content", type="faq",
        status=update_data.status or "active"
    )

@router.delete("/{id}")
async def delete_knowledge(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Delete a knowledge entry."""
    return {"status": "success"}

@router.post("/{id}/approve", response_model=KnowledgeResponse)
async def approve_knowledge(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Approve a pending correction."""
    return KnowledgeResponse(
        id=id, business_id=business_id, title="Approved", content="content",
        type="faq", status="active"
    )

@router.post("/{id}/archive", response_model=KnowledgeResponse)
async def archive_knowledge(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Archive a knowledge entry."""
    return KnowledgeResponse(
        id=id, business_id=business_id, title="Archived", content="content",
        type="faq", status="archived"
    )

@router.post("/corrections", response_model=KnowledgeResponse)
async def create_correction(
    correction: CorrectionCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Manually capture a correction."""
    return KnowledgeResponse(
        id="temp_correction", business_id=business_id, title="Correction",
        content=correction.correction_text, type="best_practice", status="pending"
    )

@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    search_req: SearchRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Search knowledge base (semantic search with query text)."""
    return SearchResponse(results=[])
