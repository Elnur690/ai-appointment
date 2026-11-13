from typing import Annotated, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import require_role
from app.models.business import Business
from app.models.saas import Plan
from app.models.subscription import Subscription
from app.models.appointment import Appointment
from app.models.conversation import Message
from app.models.reseller import Reseller

router = APIRouter()


class BusinessResponse(BaseModel):
    id: str
    name: str
    owner: Optional[str] = None
    plan: Optional[str] = None
    branches: int = 0
    status: str
    custom_domain: Optional[str] = None
    reseller_id: Optional[str] = None
    created_at: Optional[str] = None


class PlanResponse(BaseModel):
    id: str
    name: str
    price: float
    max_branches: int = 1
    max_whatsapp_numbers: int = 1
    ai_message_quota: int = 1000
    message_limit: int = 1000
    allows_voice_messages: bool = False
    allows_dynamic_pricing: bool = False
    allows_winback_campaigns: bool = False
    allows_discovery: bool = False
    allows_online_payments: bool = False
    allows_gcal_sync: bool = False
    allows_apple_cal_sync: bool = False
    allows_custom_domain: bool = False
    allows_no_show_deposits: bool = False
    allows_emergency_reassignment: bool = False
    allows_omnichannel_messaging: bool = False
    allows_growth_advisor: bool = False
    allows_loyalty_program: bool = False
    allows_combo_packages: bool = False
    allows_group_bookings: bool = False
    allows_product_upsells: bool = False
    allows_geo_routing: bool = False
    allows_shift_management: bool = False
    allows_cadence_engine: bool = False
    allows_gift_vouchers: bool = False
    allows_flash_drops: bool = False
    features: Optional[dict] = None


class PlanCreate(BaseModel):
    name: str
    price: float
    max_branches: int = 1
    max_whatsapp_numbers: int = 1
    ai_message_quota: int = 1000
    message_limit: Optional[int] = None
    allows_voice_messages: bool = False
    allows_dynamic_pricing: bool = False
    allows_winback_campaigns: bool = False
    allows_discovery: bool = False
    allows_online_payments: bool = False
    allows_gcal_sync: bool = False
    allows_apple_cal_sync: bool = False
    allows_custom_domain: bool = False
    allows_no_show_deposits: bool = False
    allows_emergency_reassignment: bool = False
    allows_omnichannel_messaging: bool = False
    allows_growth_advisor: bool = False
    allows_loyalty_program: bool = False
    allows_combo_packages: bool = False
    allows_group_bookings: bool = False
    allows_product_upsells: bool = False
    allows_geo_routing: bool = False
    allows_shift_management: bool = False
    allows_cadence_engine: bool = False
    allows_gift_vouchers: bool = False
    allows_flash_drops: bool = False
    features: Optional[dict] = None


class PlanUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    allows_voice_messages: Optional[bool] = None
    allows_dynamic_pricing: Optional[bool] = None
    allows_winback_campaigns: Optional[bool] = None
    allows_discovery: Optional[bool] = None
    allows_online_payments: Optional[bool] = None
    allows_gcal_sync: Optional[bool] = None
    allows_apple_cal_sync: Optional[bool] = None
    allows_custom_domain: Optional[bool] = None
    allows_no_show_deposits: Optional[bool] = None
    allows_emergency_reassignment: Optional[bool] = None
    allows_omnichannel_messaging: Optional[bool] = None
    allows_growth_advisor: Optional[bool] = None
    allows_loyalty_program: Optional[bool] = None
    allows_combo_packages: Optional[bool] = None
    allows_group_bookings: Optional[bool] = None
    allows_product_upsells: Optional[bool] = None
    allows_geo_routing: Optional[bool] = None
    allows_shift_management: Optional[bool] = None
    allows_cadence_engine: Optional[bool] = None
    allows_gift_vouchers: Optional[bool] = None
    allows_flash_drops: Optional[bool] = None
    features: Optional[dict] = None


class BusinessStatusUpdate(BaseModel):
    status: Optional[str] = None
    custom_domain: Optional[str] = None
    plan: Optional[str] = None


class AnalyticsResponse(BaseModel):
    total_businesses: int
    active_subscriptions: int = 0
    mrr_usd: float = 0.0
    total_appointments: int = 0
    total_messages: int = 0
    total_messages_this_month: int = 0
    total_resellers: int = 0


def _plan_to_response(p: Plan) -> PlanResponse:
    quota = int(p.ai_message_quota or 1000)
    return PlanResponse(
        id=str(p.id),
        name=p.name,
        price=float(p.price),
        max_branches=p.max_branches,
        max_whatsapp_numbers=p.max_whatsapp_numbers,
        ai_message_quota=quota,
        message_limit=quota,
        allows_voice_messages=bool(p.allows_voice_messages),
        allows_dynamic_pricing=bool(p.allows_dynamic_pricing),
        allows_winback_campaigns=bool(p.allows_winback_campaigns),
        allows_discovery=bool(p.allows_discovery),
        allows_online_payments=bool(p.allows_online_payments),
        allows_gcal_sync=bool(p.allows_gcal_sync),
        allows_apple_cal_sync=bool(p.allows_apple_cal_sync),
        allows_custom_domain=bool(p.allows_custom_domain),
        allows_no_show_deposits=bool(p.allows_no_show_deposits),
        allows_emergency_reassignment=bool(p.allows_emergency_reassignment),
        allows_omnichannel_messaging=bool(p.allows_omnichannel_messaging),
        allows_growth_advisor=bool(p.allows_growth_advisor),
        allows_loyalty_program=bool(p.allows_loyalty_program),
        allows_combo_packages=bool(p.allows_combo_packages),
        allows_group_bookings=bool(p.allows_group_bookings),
        allows_product_upsells=bool(p.allows_product_upsells),
        allows_geo_routing=bool(p.allows_geo_routing),
        allows_shift_management=bool(p.allows_shift_management),
        allows_cadence_engine=bool(p.allows_cadence_engine),
        allows_gift_vouchers=bool(p.allows_gift_vouchers),
        allows_flash_drops=bool(p.allows_flash_drops),
        features=p.features,
    )


def _biz_to_response(b: Business) -> BusinessResponse:
    owner_str = b.owners[0].email if getattr(b, "owners", None) else "—"
    plan_str = b.plan.name if getattr(b, "plan", None) else "Starter"
    branch_cnt = len(b.branches) if getattr(b, "branches", None) else 0
    return BusinessResponse(
        id=str(b.id),
        name=b.name,
        owner=owner_str,
        plan=plan_str,
        branches=branch_cnt,
        status=b.subscription_status if b.is_active else "suspended",
        custom_domain=b.custom_domain,
        reseller_id=str(b.reseller_id) if b.reseller_id else None,
        created_at=b.created_at.strftime("%Y-%m-%d") if b.created_at else None,
    )


@router.get("/businesses", response_model=List[BusinessResponse])
async def list_businesses(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
):
    """List all businesses on the platform from PostgreSQL."""
    stmt = (
        select(Business)
        .options(
            selectinload(Business.owners),
            selectinload(Business.plan),
            selectinload(Business.branches),
        )
        .offset(skip)
        .limit(limit)
        .order_by(Business.created_at.desc())
    )
    res = await db.execute(stmt)
    return [_biz_to_response(b) for b in res.scalars().all()]


@router.get("/businesses/{id}", response_model=BusinessResponse)
async def get_business(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Get business details by ID."""
    stmt = (
        select(Business)
        .where(Business.id == UUID(id))
        .options(
            selectinload(Business.owners),
            selectinload(Business.plan),
            selectinload(Business.branches),
        )
    )
    biz = (await db.execute(stmt)).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    return _biz_to_response(biz)


@router.put("/businesses/{id}/status", response_model=BusinessResponse)
async def update_business_status(
    id: str,
    status_update: BusinessStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Approve, suspend, or assign white-label domain to a business."""
    stmt = (
        select(Business)
        .where(Business.id == UUID(id))
        .options(
            selectinload(Business.owners),
            selectinload(Business.plan),
            selectinload(Business.branches),
        )
    )
    biz = (await db.execute(stmt)).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")
    if status_update.status:
        biz.is_active = status_update.status.lower() != "suspended"
        biz.subscription_status = status_update.status.lower()
    if status_update.custom_domain is not None:
        biz.custom_domain = status_update.custom_domain.strip().lower() or None
    if status_update.plan:
        plan_obj = (
            await db.execute(select(Plan).where(Plan.name == status_update.plan))
        ).scalar_one_or_none()
        if plan_obj:
            biz.plan_id = plan_obj.id
            biz.plan = plan_obj
    await db.flush()
    return _biz_to_response(biz)


@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """List all subscription plans from PostgreSQL."""
    res = await db.execute(select(Plan).order_by(Plan.price.asc()))
    return [_plan_to_response(p) for p in res.scalars().all()]


@router.post("/plans", response_model=PlanResponse)
async def create_plan(
    plan_in: PlanCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Create a new subscription plan with all 20 entitlement flags."""
    dump = plan_in.model_dump()
    msg_limit = dump.pop("message_limit", None)
    if msg_limit is not None:
        dump["ai_message_quota"] = msg_limit
    plan = Plan(**dump, is_active=True)
    db.add(plan)
    await db.flush()
    return _plan_to_response(plan)


@router.put("/plans/{id}", response_model=PlanResponse)
async def update_plan(
    id: str,
    plan_in: PlanUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Update a subscription plan."""
    plan = (await db.execute(select(Plan).where(Plan.id == UUID(id)))).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    for k, v in plan_in.model_dump(exclude_unset=True).items():
        setattr(plan, k, v)
    await db.flush()
    return _plan_to_response(plan)


@router.get("/subscriptions")
async def list_subscriptions(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """List all business subscriptions from PostgreSQL."""
    stmt = (
        select(Business)
        .options(selectinload(Business.plan))
        .order_by(Business.created_at.desc())
    )
    businesses = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(b.id),
            "business": b.name,
            "plan": b.plan.name if b.plan else "Starter",
            "status": b.subscription_status if b.is_active else "suspended",
            "period": "Monthly",
            "messagesUsed": f"0 / {b.plan.ai_message_quota if b.plan else 1000}",
        }
        for b in businesses
    ]


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_platform_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Get real platform-wide analytics from PostgreSQL."""
    biz_cnt = (await db.execute(select(func.count(Business.id)))).scalar_one()
    active_cnt = (
        await db.execute(select(func.count(Business.id)).where(Business.is_active == True))
    ).scalar_one()
    appt_cnt = (await db.execute(select(func.count(Appointment.id)))).scalar_one()
    msg_cnt = (await db.execute(select(func.count(Message.id)))).scalar_one()
    res_cnt = (await db.execute(select(func.count(Reseller.id)))).scalar_one()
    mrr_val = (
        await db.execute(
            select(func.coalesce(func.sum(Plan.price), 0))
            .select_from(Business)
            .join(Plan, Business.plan_id == Plan.id)
            .where(Business.is_active == True)
        )
    ).scalar_one()
    return AnalyticsResponse(
        total_businesses=int(biz_cnt or 0),
        active_subscriptions=int(active_cnt or 0),
        mrr_usd=float(mrr_val or 0.0),
        total_appointments=int(appt_cnt or 0),
        total_messages=int(msg_cnt or 0),
        total_messages_this_month=int(msg_cnt or 0),
        total_resellers=int(res_cnt or 0),
    )


class ActivateModelRequest(BaseModel):
    provider: str
    model_id: str
    api_key: str | None = None


@router.get("/ai-models/discover")
async def discover_latest_source_models(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Discover latest AI models directly from Google, Anthropic, and OpenAI official source REST APIs."""
    from app.services.ai_model_discovery_service import AIModelDiscoveryService
    return await AIModelDiscoveryService.discover_all_source_models()


@router.post("/ai-models/activate")
async def activate_model_version(
    req: ActivateModelRequest,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Activate a specific model version or rotate API keys live with zero downtime."""
    from app.services.ai_registry import AIRegistryService
    AIRegistryService.update_provider_config(provider=req.provider, model_name=req.model_id, api_key=req.api_key)
    return {
        "status": "success",
        "message": f"Successfully activated '{req.model_id}' for provider '{req.provider}' live with zero downtime.",
        "active_config": AIRegistryService.get_provider_config(req.provider),
    }
