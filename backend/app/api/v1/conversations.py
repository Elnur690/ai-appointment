from typing import Annotated, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class ConversationBase(BaseModel):
    customer_phone: str
    branch_id: str
    ai_active: bool

class ConversationResponse(ConversationBase):
    id: str
    business_id: str
    status: str

class ConversationDetailResponse(ConversationResponse):
    messages: List[dict] = []

@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    ai_active: bool | None = None,
    branch_id: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List conversations."""
    return []

@router.get("/{id}", response_model=ConversationDetailResponse)
async def get_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get conversation details with messages."""
    return ConversationDetailResponse(
        id=id, business_id=business_id, customer_phone="123", branch_id="default",
        ai_active=True, status="open", messages=[]
    )

@router.post("/{id}/takeover", response_model=ConversationResponse)
async def takeover_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Take over conversation from AI (ai_active=False)."""
    return ConversationResponse(
        id=id, business_id=business_id, customer_phone="123", branch_id="default",
        ai_active=False, status="open"
    )

@router.post("/{id}/activate-ai", response_model=ConversationResponse)
async def activate_ai(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Re-activate AI for a conversation."""
    return ConversationResponse(
        id=id, business_id=business_id, customer_phone="123", branch_id="default",
        ai_active=True, status="open"
    )
