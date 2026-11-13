from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.conversation import Conversation, Message, MessageDirection

router = APIRouter()


class MessageSendRequest(BaseModel):
    content: str


class ConversationResponse(BaseModel):
    id: str
    business_id: str
    customer_phone: str
    customer_name: str | None = None
    branch_id: str
    ai_active: bool
    status: str
    last_message: str | None = None


class ConversationDetailResponse(ConversationResponse):
    messages: List[dict] = []


def _to_response(c: Conversation, last_msg: str | None = None) -> ConversationResponse:
    return ConversationResponse(
        id=str(c.id),
        business_id=str(c.business_id),
        customer_phone=c.customer.phone_number if c.customer else "Unknown",
        customer_name=c.customer.name if c.customer else None,
        branch_id=str(c.branch_id),
        ai_active=bool(c.ai_active),
        status="ai_active" if c.ai_active else "human_takeover",
        last_message=last_msg,
    )


@router.get("/", response_model=List[ConversationResponse])
async def list_conversations(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    ai_active: bool | None = None,
    branch_id: str | None = None,
):
    """List conversations from PostgreSQL."""
    stmt = (
        select(Conversation)
        .where(Conversation.business_id == UUID(business_id))
        .options(selectinload(Conversation.customer), selectinload(Conversation.messages))
    )
    if ai_active is not None:
        stmt = stmt.where(Conversation.ai_active == ai_active)
    if branch_id:
        stmt = stmt.where(Conversation.branch_id == UUID(branch_id))
    stmt = stmt.order_by(Conversation.updated_at.desc())
    res = await db.execute(stmt)
    out = []
    for c in res.scalars().all():
        last_text = c.messages[-1].content if c.messages else None
        out.append(_to_response(c, last_msg=last_text))
    return out


@router.get("/{id}", response_model=ConversationDetailResponse)
async def get_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get conversation details with messages from PostgreSQL."""
    stmt = (
        select(Conversation)
        .where(Conversation.id == UUID(id), Conversation.business_id == UUID(business_id))
        .options(selectinload(Conversation.customer), selectinload(Conversation.messages))
    )
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return ConversationDetailResponse(
        id=str(c.id),
        business_id=str(c.business_id),
        customer_phone=c.customer.phone_number if c.customer else "Unknown",
        customer_name=c.customer.name if c.customer else None,
        branch_id=str(c.branch_id),
        ai_active=bool(c.ai_active),
        status="ai_active" if c.ai_active else "human_takeover",
        messages=[
            {
                "id": str(m.id),
                "direction": m.direction.value if hasattr(m.direction, "value") else str(m.direction),
                "content": m.content,
                "created_at": m.created_at.isoformat() if m.created_at else None,
            }
            for m in c.messages
        ],
    )


@router.post("/{id}/takeover")
async def takeover_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Toggle AI / Human takeover mode on a conversation."""
    stmt = select(Conversation).where(Conversation.id == UUID(id), Conversation.business_id == UUID(business_id))
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    c.ai_active = False
    await db.flush()
    return {"status": "human_takeover", "ai_active": False}


@router.post("/{id}/release")
async def release_conversation(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Release conversation back to AI agent."""
    stmt = select(Conversation).where(Conversation.id == UUID(id), Conversation.business_id == UUID(business_id))
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    c.ai_active = True
    await db.flush()
    return {"status": "ai_active", "ai_active": True}


@router.post("/{id}/messages")
async def send_manual_message(
    id: str,
    message: MessageSendRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Send manual message as staff during takeover."""
    stmt = select(Conversation).where(Conversation.id == UUID(id), Conversation.business_id == UUID(business_id))
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Conversation not found")
    c.ai_active = False
    msg = Message(
        conversation_id=c.id,
        direction=MessageDirection.outbound,
        content=message.content.strip(),
        message_type="text",
    )
    db.add(msg)
    await db.flush()
    return {"status": "sent", "id": str(msg.id), "content": msg.content}
