from typing import Annotated, Any, List
from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class PaymentBase(BaseModel):
    appointment_id: str
    amount: float
    method: str
    branch_id: str | None = None

class PaymentCreate(PaymentBase):
    pass

class PaymentResponse(PaymentBase):
    id: str
    business_id: str
    status: str

class RevenueSummaryResponse(BaseModel):
    total_revenue: float
    by_branch: dict[str, float] = {}

@router.post("/", response_model=PaymentResponse)
async def log_payment(
    payment: PaymentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Log a cash payment."""
    return PaymentResponse(
        id="temp", business_id=business_id, status="completed", **payment.model_dump()
    )

@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    start_date: date | None = None,
    end_date: date | None = None,
    method: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List payments with optional filters."""
    return []

@router.get("/summary", response_model=RevenueSummaryResponse)
async def revenue_summary(
    start_date: date | None = None,
    end_date: date | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get revenue summary."""
    return RevenueSummaryResponse(total_revenue=0.0)
