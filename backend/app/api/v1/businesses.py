from typing import Annotated, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import require_role, get_business_context

router = APIRouter()

class BusinessResponse(BaseModel):
    id: str
    name: str
    settings: dict = {}

class BusinessUpdate(BaseModel):
    name: str | None = None
    settings: dict | None = None

class BusinessAnalyticsResponse(BaseModel):
    appointments_this_month: int
    revenue_this_month: float

@router.get("/", response_model=BusinessResponse)
async def get_own_business(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("business_owner"))],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get details of the currently authenticated business."""
    # TODO: Implement fetching business
    return BusinessResponse(id=business_id, name="My Business")

@router.put("/", response_model=BusinessResponse)
async def update_own_business(
    update_data: BusinessUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("business_owner"))],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Update settings of the currently authenticated business."""
    # TODO: Implement updating business
    return BusinessResponse(id=business_id, name=update_data.name or "My Business")

@router.get("/analytics", response_model=BusinessAnalyticsResponse)
async def get_business_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("business_owner"))],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get analytics for the current business."""
    # TODO: Implement analytics query
    return BusinessAnalyticsResponse(appointments_this_month=0, revenue_this_month=0.0)
