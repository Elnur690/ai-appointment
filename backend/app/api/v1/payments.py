from datetime import date, datetime, time, timezone
from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.payment import Payment, PaymentMethod, PaymentStatus

router = APIRouter()


class PaymentCreate(BaseModel):
    appointment_id: str | None = None
    amount: float
    currency: str = "AZN"
    method: str = "cash"
    status: str | None = None
    notes: str | None = None


class PaymentResponse(BaseModel):
    id: str
    business_id: str
    appointment_id: str | None = None
    customer: str = "Walk-In / Direct"
    gateway: str = "Cash"
    amount: str
    amount_value: float
    currency: str = "AZN"
    method: str = "cash"
    status: str
    notes: str | None = None
    created_at: str | None = None


class RevenueSummaryResponse(BaseModel):
    total_revenue: float
    count: int = 0
    currency: str = "AZN"


def _to_response(p: Payment) -> PaymentResponse:
    method_val = p.method.value if hasattr(p.method, "value") else str(p.method)
    status_val = p.status.value if hasattr(p.status, "value") else str(p.status)
    amt_float = float(p.amount)
    curr = p.currency or "AZN"
    return PaymentResponse(
        id=str(p.id),
        business_id=str(p.business_id),
        appointment_id=str(p.appointment_id) if p.appointment_id else None,
        customer=p.notes or "Direct Checkout",
        gateway=method_val.capitalize(),
        amount=f"{amt_float:.2f} {curr}",
        amount_value=amt_float,
        currency=curr,
        method=method_val,
        status=status_val,
        notes=p.notes,
        created_at=p.created_at.isoformat() if p.created_at else None,
    )


@router.post("/", response_model=PaymentResponse)
async def log_payment(
    payment: PaymentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Log a payment in PostgreSQL."""
    method_str = (payment.method or "cash").lower()
    if method_str not in {"cash", "payriff", "epoint"}:
        method_str = "cash"
    row = Payment(
        business_id=UUID(business_id),
        appointment_id=UUID(payment.appointment_id) if payment.appointment_id else None,
        amount=payment.amount,
        currency=payment.currency or "AZN",
        method=PaymentMethod(method_str),
        status=PaymentStatus.completed,
        notes=payment.notes,
    )
    db.add(row)
    await db.flush()
    return _to_response(row)


@router.get("/", response_model=List[PaymentResponse])
async def list_payments(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    start_date: date | None = None,
    end_date: date | None = None,
    method: str | None = None,
):
    """List payments from PostgreSQL with optional filters."""
    stmt = select(Payment).where(Payment.business_id == UUID(business_id))
    if start_date:
        stmt = stmt.where(Payment.created_at >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
    if end_date:
        stmt = stmt.where(Payment.created_at <= datetime.combine(end_date, time.max, tzinfo=timezone.utc))
    if method:
        stmt = stmt.where(Payment.method == PaymentMethod(method.lower()))
    stmt = stmt.order_by(Payment.created_at.desc())
    res = await db.execute(stmt)
    return [_to_response(p) for p in res.scalars().all()]


@router.get("/summary", response_model=RevenueSummaryResponse)
async def revenue_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    start_date: date | None = None,
    end_date: date | None = None,
):
    """Get real revenue summary from PostgreSQL."""
    stmt = select(
        func.coalesce(func.sum(Payment.amount), 0),
        func.count(Payment.id),
    ).where(
        Payment.business_id == UUID(business_id),
        Payment.status == PaymentStatus.completed,
    )
    if start_date:
        stmt = stmt.where(Payment.created_at >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
    if end_date:
        stmt = stmt.where(Payment.created_at <= datetime.combine(end_date, time.max, tzinfo=timezone.utc))
    row = (await db.execute(stmt)).one()
    return RevenueSummaryResponse(total_revenue=float(row[0] or 0.0), count=int(row[1] or 0))
