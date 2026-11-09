from typing import Annotated, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_role
from app.core.security import hash_password
from app.models.reseller import Reseller, ResellerPayout
from app.models.business import Business
from app.models.saas import Plan
from app.services.reseller_service import ResellerService

router = APIRouter()
reseller_service = ResellerService()


class ResellerCreate(BaseModel):
    name: str
    company_name: Optional[str] = None
    email: EmailStr
    phone: Optional[str] = None
    password: str = "Partner123!"
    referral_code: str
    commission_rate_percent: float = 20.0
    white_label_domain: Optional[str] = None


class ResellerUpdate(BaseModel):
    name: Optional[str] = None
    company_name: Optional[str] = None
    commission_rate_percent: Optional[float] = None
    white_label_domain: Optional[str] = None
    is_active: Optional[bool] = None


class ResellerPayoutCreate(BaseModel):
    amount_azn: float
    payment_method: str = "bank_transfer"
    reference_note: Optional[str] = None


class ResellerResponse(BaseModel):
    id: str
    name: str
    company_name: Optional[str] = None
    email: str
    phone: Optional[str] = None
    referral_code: str
    referral_url: str
    commission_rate_percent: float
    white_label_domain: Optional[str] = None
    referred_businesses_count: int = 0
    active_businesses_count: int = 0
    total_mrr_generated_azn: float = 0.0
    monthly_commission_azn: float = 0.0
    total_earned_azn: float = 0.0
    total_paid_azn: float = 0.0
    pending_payout_azn: float = 0.0
    is_active: bool = True


async def _build_reseller_response(reseller: Reseller, db: AsyncSession) -> ResellerResponse:
    stmt = (
        select(Business, Plan.price)
        .outerjoin(Plan, Business.plan_id == Plan.id)
        .where(Business.reseller_id == reseller.id)
    )
    rows = (await db.execute(stmt)).all()
    referred_list = [
        {
            "id": str(biz.id),
            "name": biz.name,
            "status": "active" if biz.is_active else "suspended",
            "plan_price_azn": float(price or 79.0),
        }
        for biz, price in rows
    ]
    summary = reseller_service.evaluate_reseller_portfolio(
        reseller_id=reseller.id,
        reseller_name=reseller.name,
        referral_code=reseller.referral_code,
        commission_rate_percent=float(reseller.commission_rate_percent),
        referred_businesses=referred_list,
        total_earned_historical_azn=float(reseller.total_earned_azn or 0.0),
        total_paid_historical_azn=float(reseller.total_paid_azn or 0.0),
        company_name=reseller.company_name,
        white_label_domain=reseller.white_label_domain,
    )
    return ResellerResponse(
        id=str(reseller.id),
        name=reseller.name,
        company_name=reseller.company_name,
        email=reseller.email,
        phone=reseller.phone,
        referral_code=summary.referral_code,
        referral_url=summary.referral_url,
        commission_rate_percent=summary.commission_rate_percent,
        white_label_domain=reseller.white_label_domain,
        referred_businesses_count=summary.referred_businesses_count,
        active_businesses_count=summary.active_businesses_count,
        total_mrr_generated_azn=summary.total_mrr_generated_azn,
        monthly_commission_azn=summary.monthly_commission_azn,
        total_earned_azn=summary.total_earned_azn,
        total_paid_azn=summary.total_paid_azn,
        pending_payout_azn=summary.pending_payout_azn,
        is_active=reseller.is_active,
    )


@router.get("/", response_model=List[ResellerResponse])
async def list_resellers(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """List all reseller / agency partners with live MRR and commission analytics."""
    res = await db.execute(select(Reseller).order_by(Reseller.created_at.desc()))
    resellers = list(res.scalars().all())
    return [await _build_reseller_response(r, db) for r in resellers]


@router.post("/", response_model=ResellerResponse, status_code=status.HTTP_201_CREATED)
async def create_reseller(
    data: ResellerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Create a new reseller / agency partner."""
    norm_code = reseller_service.normalize_referral_code(data.referral_code)
    existing = await db.execute(
        select(Reseller).where((Reseller.email == data.email) | (Reseller.referral_code == norm_code))
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Reseller email or referral code already exists")

    reseller = Reseller(
        name=data.name,
        company_name=data.company_name,
        email=data.email,
        phone=data.phone,
        password_hash=hash_password(data.password),
        referral_code=norm_code,
        commission_rate_percent=data.commission_rate_percent,
        white_label_domain=data.white_label_domain,
        is_active=True,
    )
    db.add(reseller)
    await db.flush()
    return await _build_reseller_response(reseller, db)


@router.put("/{reseller_id}", response_model=ResellerResponse)
async def update_reseller(
    reseller_id: UUID,
    data: ResellerUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Update reseller commission rate, white-label domain, or active status."""
    reseller = (await db.execute(select(Reseller).where(Reseller.id == reseller_id))).scalar_one_or_none()
    if not reseller:
        raise HTTPException(status_code=404, detail="Reseller not found")

    if data.name is not None:
        reseller.name = data.name
    if data.company_name is not None:
        reseller.company_name = data.company_name
    if data.commission_rate_percent is not None:
        reseller.commission_rate_percent = data.commission_rate_percent
    if data.white_label_domain is not None:
        reseller.white_label_domain = data.white_label_domain
    if data.is_active is not None:
        reseller.is_active = data.is_active

    await db.flush()
    return await _build_reseller_response(reseller, db)


@router.post("/{reseller_id}/payouts")
async def record_reseller_payout(
    reseller_id: UUID,
    payout_req: ResellerPayoutCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Record a commission payout to a reseller partner."""
    reseller = (await db.execute(select(Reseller).where(Reseller.id == reseller_id))).scalar_one_or_none()
    if not reseller:
        raise HTTPException(status_code=404, detail="Reseller not found")

    if payout_req.amount_azn <= 0:
        raise HTTPException(status_code=400, detail="Payout amount must be positive")

    payout = ResellerPayout(
        reseller_id=reseller.id,
        amount_azn=payout_req.amount_azn,
        payment_method=payout_req.payment_method,
        reference_note=payout_req.reference_note,
        status="completed",
    )
    reseller.total_paid_azn = float(reseller.total_paid_azn or 0.0) + payout_req.amount_azn
    db.add(payout)
    await db.flush()
    return {
        "status": "success",
        "payout_id": str(payout.id),
        "amount_azn": payout_req.amount_azn,
        "total_paid_azn": float(reseller.total_paid_azn),
    }
