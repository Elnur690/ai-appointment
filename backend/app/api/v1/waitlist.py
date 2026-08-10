from datetime import date, datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.waitlist import WaitlistEntry, WaitlistStatus
from app.services.waitlist_service import WaitlistService

router = APIRouter()

class WaitlistCreate(BaseModel):
    branch_id: UUID
    customer_id: UUID
    service_id: UUID
    preferred_date: date
    staff_id: UUID | None = None
    notes: str | None = None

class WaitlistResponse(BaseModel):
    id: UUID
    business_id: UUID
    branch_id: UUID
    customer_id: UUID
    service_id: UUID
    preferred_date: date
    status: WaitlistStatus
    notes: str | None
    created_at: datetime

    class Config:
        from_attributes = True

@router.get("/", response_model=list[WaitlistResponse])
async def list_waitlist(
    db: AsyncSession = Depends(get_db),
    business_id: UUID = Depends(get_business_context),
    current_user: dict = Depends(get_current_active_user),
):
    """List waitlist entries for a business."""
    stmt = select(WaitlistEntry).where(WaitlistEntry.business_id == business_id).order_by(WaitlistEntry.created_at.desc())
    res = await db.execute(stmt)
    return list(res.scalars().all())

@router.post("/", response_model=WaitlistResponse, status_code=status.HTTP_201_CREATED)
async def create_waitlist_entry(
    data: WaitlistCreate,
    db: AsyncSession = Depends(get_db),
    business_id: UUID = Depends(get_business_context),
    current_user: dict = Depends(get_current_active_user),
):
    """Add a customer to appointment waitlist."""
    service = WaitlistService(db, business_id)
    return await service.add_to_waitlist(
        branch_id=data.branch_id,
        customer_id=data.customer_id,
        service_id=data.service_id,
        preferred_date=data.preferred_date,
        staff_id=data.staff_id,
        notes=data.notes,
    )

@router.get("/no-show-check/{customer_id}")
async def check_no_show_penalty(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    business_id: UUID = Depends(get_business_context),
    current_user: dict = Depends(get_current_active_user),
):
    """Check if customer has 2+ no-shows requiring deposit or staff approval."""
    service = WaitlistService(db, business_id)
    has_penalty = await service.check_no_show_penalty(customer_id)
    return {"customer_id": customer_id, "requires_deposit": has_penalty}
