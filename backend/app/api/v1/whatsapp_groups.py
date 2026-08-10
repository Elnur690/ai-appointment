from typing import Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.whatsapp import WhatsAppGroup, WhatsAppGroupScope

router = APIRouter()

class WhatsAppGroupCreate(BaseModel):
    group_jid: str
    group_name: str | None = None
    scope: WhatsAppGroupScope = WhatsAppGroupScope.single_branch
    branch_id: UUID | None = None

class WhatsAppGroupResponse(BaseModel):
    id: UUID
    business_id: UUID
    branch_id: UUID | None
    group_jid: str
    group_name: str | None
    scope: WhatsAppGroupScope
    is_active: bool

    class Config:
        from_attributes = True

@router.get("/", response_model=list[WhatsAppGroupResponse])
async def list_whatsapp_groups(
    db: AsyncSession = Depends(get_db),
    business_id: UUID = Depends(get_business_context),
    current_user: dict = Depends(get_current_active_user),
):
    """List registered internal WhatsApp groups for a business."""
    stmt = select(WhatsAppGroup).where(WhatsAppGroup.business_id == business_id)
    result = await db.execute(stmt)
    return list(result.scalars().all())

@router.post("/", response_model=WhatsAppGroupResponse, status_code=status.HTTP_201_CREATED)
async def register_whatsapp_group(
    data: WhatsAppGroupCreate,
    db: AsyncSession = Depends(get_db),
    business_id: UUID = Depends(get_business_context),
    current_user: dict = Depends(get_current_active_user),
):
    """Register bot into an internal staff/owner WhatsApp group."""
    group = WhatsAppGroup(
        business_id=business_id,
        branch_id=data.branch_id,
        group_jid=data.group_jid,
        group_name=data.group_name,
        scope=data.scope,
        is_active=True,
    )
    db.add(group)
    await db.commit()
    await db.refresh(group)
    return group

@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_whatsapp_group(
    group_id: UUID,
    db: AsyncSession = Depends(get_db),
    business_id: UUID = Depends(get_business_context),
    current_user: dict = Depends(get_current_active_user),
):
    """Unregister/delete an internal WhatsApp group."""
    stmt = select(WhatsAppGroup).where(
        WhatsAppGroup.id == group_id,
        WhatsAppGroup.business_id == business_id,
    )
    result = await db.execute(stmt)
    group = result.scalar_one_or_none()
    if not group:
        raise HTTPException(status_code=404, detail="WhatsApp group not found")
    
    await db.delete(group)
    await db.commit()
