from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.core.dependencies import require_role
from app.core.security import hash_password
from app.models.business import Business, BusinessOwner, Branch
from app.models.saas import Plan, PlatformConfig, RefundRequest, DEFAULT_PLATFORM_GATEWAYS, DEFAULT_REFUND_RULES
from app.models.appointment import Appointment, AppointmentStatus
from app.models.customer import Customer
from app.models.conversation import Conversation, Message, MessageDirection
from app.models.payment import Payment, PaymentStatus
from app.models.reseller import Reseller

router = APIRouter()

# Official blended per-1M token cost in USD (input + output weighted)
MODEL_COST_PER_1M_TOKENS_USD = {
    "gemini-3.5-flash": 0.45,
    "claude-3-7-sonnet": 9.00,
    "gpt-4o": 6.25,
}
USD_TO_AZN_RATE = 1.70


class BusinessCreate(BaseModel):
    business_name: str
    owner_name: Optional[str] = None
    email: str
    password: str
    phone: Optional[str] = None
    category: Optional[str] = None
    plan: Optional[str] = None
    plan_id: Optional[str] = None
    status: str = "trial"
    trial_days: Optional[int] = None
    custom_domain: Optional[str] = None
    trial_features_override: Optional[dict[str, bool]] = None


class BusinessResponse(BaseModel):
    id: str
    name: str
    owner: Optional[str] = None
    plan: Optional[str] = None
    branches: int = 0
    status: str
    trial_ends_at: Optional[str] = None
    trial_days_remaining: int = 0
    trial_features_override: Optional[dict] = None
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
    allows_free_trial: bool = True
    trial_days: int = 14
    trial_features: Optional[dict] = None
    allows_whatsapp: bool = True
    allows_instagram: bool = False
    allows_telegram: bool = False
    allows_voice_messages: bool = False
    allows_dynamic_pricing: bool = False
    allows_winback_campaigns: bool = False
    allows_discovery: bool = False
    allows_online_payments: bool = False
    allowed_payment_providers: list[str] = ["cash", "payriff", "epoint"]
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
    allows_branch_level_ai_tone: bool = False
    features: Optional[dict] = None


class PlanCreate(BaseModel):
    name: str
    price: float
    max_branches: int = 1
    max_whatsapp_numbers: int = 1
    ai_message_quota: int = 1000
    message_limit: Optional[int] = None
    allows_free_trial: bool = True
    trial_days: int = 14
    trial_features: Optional[dict] = None
    allows_whatsapp: bool = True
    allows_instagram: bool = False
    allows_telegram: bool = False
    allows_voice_messages: bool = False
    allows_dynamic_pricing: bool = False
    allows_winback_campaigns: bool = False
    allows_discovery: bool = False
    allows_online_payments: bool = False
    allowed_payment_providers: list[str] = ["cash", "payriff", "epoint"]
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
    allows_branch_level_ai_tone: bool = False
    features: Optional[dict] = None


class PlanUpdate(BaseModel):
    name: str | None = None
    price: float | None = None
    max_branches: Optional[int] = None
    max_whatsapp_numbers: Optional[int] = None
    ai_message_quota: Optional[int] = None
    message_limit: Optional[int] = None
    allows_free_trial: Optional[bool] = None
    trial_days: Optional[int] = None
    trial_features: Optional[dict] = None
    allows_whatsapp: Optional[bool] = None
    allows_instagram: Optional[bool] = None
    allows_telegram: Optional[bool] = None
    allows_voice_messages: Optional[bool] = None
    allows_dynamic_pricing: Optional[bool] = None
    allows_winback_campaigns: Optional[bool] = None
    allows_discovery: Optional[bool] = None
    allows_online_payments: Optional[bool] = None
    allowed_payment_providers: Optional[list[str]] = None
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
    allows_branch_level_ai_tone: Optional[bool] = None
    features: Optional[dict] = None


class BusinessStatusUpdate(BaseModel):
    status: Optional[str] = None
    custom_domain: Optional[str] = None
    plan: Optional[str] = None
    trial_days: Optional[int] = None
    trial_features_override: Optional[dict] = None


class PaymentGatewayToggleRequest(BaseModel):
    enabled: bool
    name: Optional[str] = None
    description: Optional[str] = None


class BusinessAISpendItem(BaseModel):
    business_id: str
    business_name: str
    owner_email: str
    plan_name: str
    assigned_model: str
    status: str
    trial_days_remaining: int = 0
    total_messages: int = 0
    inbound_messages: int = 0
    ai_replies: int = 0
    tokens_used: int = 0
    ai_spend_usd: float = 0.0
    ai_spend_azn: float = 0.0
    appointments_count: int = 0
    revenue_azn: float = 0.0
    plan_price_azn: float = 0.0
    net_margin_azn: float = 0.0


class AnalyticsResponse(BaseModel):
    total_businesses: int
    active_subscriptions: int = 0
    trial_businesses: int = 0
    suspended_businesses: int = 0
    mrr_usd: float = 0.0
    mrr_azn: float = 0.0
    arr_azn: float = 0.0
    total_settled_revenue_azn: float = 0.0
    total_appointments: int = 0
    completed_appointments: int = 0
    cancelled_appointments: int = 0
    pending_appointments: int = 0
    total_customers: int = 0
    total_messages: int = 0
    inbound_messages: int = 0
    outbound_ai_messages: int = 0
    total_messages_this_month: int = 0
    total_resellers: int = 0
    total_ai_tokens_used: int = 0
    total_ai_spend_usd: float = 0.0
    total_ai_spend_azn: float = 0.0
    net_platform_margin_azn: float = 0.0
    ai_spend_per_business: List[BusinessAISpendItem] = []


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
        allows_free_trial=bool(getattr(p, "allows_free_trial", True)),
        trial_days=int(getattr(p, "trial_days", 14) or 0),
        trial_features=getattr(p, "trial_features", None) or {},
        allows_whatsapp=bool(getattr(p, "allows_whatsapp", True)),
        allows_instagram=bool(getattr(p, "allows_instagram", False) or p.allows_omnichannel_messaging),
        allows_telegram=bool(getattr(p, "allows_telegram", False) or p.allows_omnichannel_messaging),
        allows_voice_messages=bool(p.allows_voice_messages),
        allows_dynamic_pricing=bool(p.allows_dynamic_pricing),
        allows_winback_campaigns=bool(p.allows_winback_campaigns),
        allows_discovery=bool(p.allows_discovery),
        allows_online_payments=bool(p.allows_online_payments),
        allowed_payment_providers=list(getattr(p, "allowed_payment_providers", None) or ["cash", "payriff", "epoint"]),
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
        allows_branch_level_ai_tone=bool(p.allows_branch_level_ai_tone),
        features=p.features,
    )


def _calc_trial_days_remaining(b: Business) -> int:
    if not getattr(b, "trial_ends_at", None):
        return 14 if b.subscription_status == "trial" else 0
    now_utc = datetime.now(timezone.utc)
    end_dt = b.trial_ends_at if b.trial_ends_at.tzinfo else b.trial_ends_at.replace(tzinfo=timezone.utc)
    return max(0, (end_dt - now_utc).days)


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
        trial_ends_at=b.trial_ends_at.strftime("%Y-%m-%d") if getattr(b, "trial_ends_at", None) else None,
        trial_days_remaining=_calc_trial_days_remaining(b),
        trial_features_override=getattr(b, "trial_features_override", None) or {},
        custom_domain=b.custom_domain,
        reseller_id=str(b.reseller_id) if b.reseller_id else None,
        created_at=b.created_at.strftime("%Y-%m-%d") if b.created_at else None,
    )


async def _get_or_create_platform_config(db: AsyncSession) -> PlatformConfig:
    cfg = (
        await db.execute(select(PlatformConfig).where(PlatformConfig.config_key == "global"))
    ).scalar_one_or_none()
    if not cfg:
        cfg = PlatformConfig(
            config_key="global",
            payment_gateways={k: dict(v) for k, v in DEFAULT_PLATFORM_GATEWAYS.items()},
        )
        db.add(cfg)
        await db.flush()
    else:
        merged = {k: dict(v) for k, v in DEFAULT_PLATFORM_GATEWAYS.items()}
        if isinstance(cfg.payment_gateways, dict):
            for k, v in cfg.payment_gateways.items():
                norm_k = "paymegate" if k == "paymengate" else k
                if norm_k in merged and isinstance(v, dict):
                    merged[norm_k].update(v)
                    merged[norm_k]["provider"] = norm_k
                    if norm_k == "paymegate":
                        merged[norm_k]["name"] = "Paymegate Payment Gateway"
        cfg.payment_gateways = merged
    return cfg


@router.get("/payment-gateways")
async def list_platform_payment_gateways(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """List all platform payment gateways (Cash, Suby.fi, Payriff, EPoint) and their enabled + .env status."""
    cfg = await _get_or_create_platform_config(db)
    order = ["cash", "suby", "payriff", "epoint"]

    def _mask_secret(val: str) -> str:
        s = (val or "").strip()
        if not s or s.startswith("change_me"):
            return ""
        return f"••••{s[-4:]}" if len(s) >= 4 else "••••"

    results = []
    for k in order:
        if k not in cfg.payment_gateways:
            continue
        item = dict(cfg.payment_gateways[k])
        if k == "suby":
            masked = _mask_secret(settings.SUBY_API_KEY)
            item["env_configured"] = bool(masked)
            item["env_hint"] = masked
        elif k in {"payriff", "epoint"}:
            item["env_configured"] = True
            item["env_hint"] = "Business Dashboard"
        else:
            item["env_configured"] = True
            item["env_hint"] = ""
        results.append(item)
    return results


class AdminPaymentTestRequest(BaseModel):
    amount: float
    currency: str = "AZN"
    description: Optional[str] = None


@router.post("/payment-gateways/test")
async def test_live_payment_checkout(
    req: AdminPaymentTestRequest,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Create a live Suby.fi checkout session for any amount (auto-converting AZN -> USD at live FX rate)."""
    from decimal import Decimal
    from uuid import uuid4
    from app.integrations.payments.suby import SubyAdapter, convert_azn_to_usd
    # Disabled: from app.integrations.payments.creem import CreemAdapter

    if req.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than 0")
    if not (settings.SUBY_API_KEY or "").strip():
        raise HTTPException(status_code=400, detail="SUBY_API_KEY is not set in .env")

    orig_currency = (req.currency or "AZN").strip().upper()
    if orig_currency not in {"AZN", "USD", "EUR"}:
        orig_currency = "AZN"

    orig_amount = Decimal(str(req.amount)).quantize(Decimal("0.01"))
    if orig_currency == "AZN":
        usd_amount, fx_rate = await convert_azn_to_usd(orig_amount)
    else:
        usd_amount, fx_rate = orig_amount, Decimal("1.0")

    test_payment_id = uuid4()
    res = await SubyAdapter().create_payment_link(
        payment_id=test_payment_id,
        amount=orig_amount,
        currency=orig_currency,
        description=req.description or f"Randevu.vip Live Test ({orig_amount} {orig_currency})",
        merchant_config={
            "mode": "payment",
            "customer_email": user.get("email") or settings.SAAS_ADMIN_EMAIL,
            "metadata": {"type": "admin_test"},
        },
        return_url=f"https://admin.{settings.PLATFORM_DOMAIN}/payment-gateways",
    )

    return {
        "checkout_url": res.payment_url,
        "order_uuid": res.transaction_id,
        "original_amount": float(orig_amount),
        "original_currency": orig_currency,
        "usd_amount": float(usd_amount),
        "fx_rate": float(fx_rate),
    }


@router.put("/payment-gateways/{provider}")
async def toggle_platform_payment_gateway(
    provider: str,
    req: PaymentGatewayToggleRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Enable or disable a payment gateway platform-wide (cash, payriff, paymegate)."""
    prov = provider.lower().strip()
    if prov == "paymengate":
        prov = "paymegate"
    if prov not in DEFAULT_PLATFORM_GATEWAYS:
        raise HTTPException(status_code=404, detail=f"Unknown payment gateway: {provider}")

    cfg = await _get_or_create_platform_config(db)
    updated_map = {k: dict(v) for k, v in cfg.payment_gateways.items()}
    entry = dict(updated_map.get(prov, DEFAULT_PLATFORM_GATEWAYS[prov]))
    entry["enabled"] = bool(req.enabled)
    if req.name is not None:
        entry["name"] = req.name
    if req.description is not None:
        entry["description"] = req.description
    updated_map[prov] = entry
    cfg.payment_gateways = updated_map
    flag_modified(cfg, "payment_gateways")
    await db.flush()
    return entry


class RefundRulesUpdate(BaseModel):
    auto_refund_enabled: bool = True
    auto_refund_window_hours: int = 48
    auto_refund_max_amount_azn: float = 100.0
    require_reason: bool = True
    allow_business_self_cancel: bool = True


class RefundDecisionRequest(BaseModel):
    admin_note: Optional[str] = None


class SupportSettingsUpdate(BaseModel):
    support_whatsapp_number: Optional[str] = None


@router.get("/support-settings")
async def get_support_settings(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Get platform WhatsApp support number configured for the landing page."""
    cfg = await _get_or_create_platform_config(db)
    return {"support_whatsapp_number": getattr(cfg, "support_whatsapp_number", None) or ""}


@router.put("/support-settings")
async def update_support_settings(
    req: SupportSettingsUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Update platform WhatsApp support number shown as floating chat button on the landing page."""
    cfg = await _get_or_create_platform_config(db)
    cfg.support_whatsapp_number = (req.support_whatsapp_number or "").strip() or None
    await db.commit()
    return {"support_whatsapp_number": cfg.support_whatsapp_number or ""}


@router.get("/refund-rules")
async def get_refund_rules(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Get platform-wide refund and auto-refund rules."""
    cfg = await _get_or_create_platform_config(db)
    merged = dict(DEFAULT_REFUND_RULES)
    if isinstance(cfg.refund_rules, dict):
        merged.update(cfg.refund_rules)
    return merged


@router.put("/refund-rules")
async def update_refund_rules(
    req: RefundRulesUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Update platform-wide refund and auto-refund rules."""
    cfg = await _get_or_create_platform_config(db)
    cfg.refund_rules = req.model_dump()
    flag_modified(cfg, "refund_rules")
    await db.commit()
    return cfg.refund_rules


@router.get("/refunds")
async def list_all_refund_requests(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """List all refund requests across all businesses for SaaS Admin review."""
    rows = (
        await db.execute(
            select(RefundRequest, Business.name)
            .join(Business, RefundRequest.business_id == Business.id)
            .order_by(RefundRequest.created_at.desc())
        )
    ).all()
    return [
        {
            "id": str(r.id),
            "business_id": str(r.business_id),
            "business_name": b_name,
            "payment_id": str(r.payment_id),
            "amount": float(r.amount),
            "currency": r.currency,
            "reason": r.reason,
            "status": r.status,
            "admin_note": r.admin_note,
            "suby_refund_id": getattr(r, "suby_refund_id", None),
            "created_at": r.created_at.isoformat() if r.created_at else None,
            "resolved_at": r.resolved_at.isoformat() if r.resolved_at else None,
        }
        for r, b_name in rows
    ]


@router.post("/refunds/{refund_id}/approve")
async def approve_refund_request(
    refund_id: str,
    req: RefundDecisionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Approve a pending refund request and trigger Suby.fi refund if paid via Suby.fi."""
    from app.models.payment import PaymentMethod
    from app.integrations.payments.suby import SubyAdapter
    # Disabled: from app.integrations.payments.creem import CreemAdapter

    rr = (await db.execute(select(RefundRequest).where(RefundRequest.id == UUID(refund_id)))).scalar_one_or_none()
    if not rr:
        raise HTTPException(status_code=404, detail="Refund request not found")
    if rr.status in {"approved", "auto_approved"}:
        return {"status": rr.status}

    payment = (await db.execute(select(Payment).where(Payment.id == rr.payment_id))).scalar_one_or_none()
    if payment and payment.method == PaymentMethod.suby and payment.gateway_transaction_id and settings.SUBY_API_KEY:
        try:
            rf_res = await SubyAdapter().create_refund(payment_id=payment.gateway_transaction_id, reason=rr.reason)
            data = rf_res.get("data") if isinstance(rf_res.get("data"), dict) else rf_res
            rr.suby_refund_id = str(data.get("id") or "")
        except Exception as exc:
            raise HTTPException(status_code=400, detail=f"Suby.fi refund failed: {exc}")

    if payment:
        payment.status = PaymentStatus.refunded
    rr.status = "approved"
    rr.admin_note = req.admin_note
    rr.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "approved", "id": str(rr.id)}


@router.post("/refunds/{refund_id}/reject")
async def reject_refund_request(
    refund_id: str,
    req: RefundDecisionRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Reject a pending refund request with an optional admin note."""
    rr = (await db.execute(select(RefundRequest).where(RefundRequest.id == UUID(refund_id)))).scalar_one_or_none()
    if not rr:
        raise HTTPException(status_code=404, detail="Refund request not found")
    rr.status = "rejected"
    rr.admin_note = req.admin_note
    rr.resolved_at = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "rejected", "id": str(rr.id)}


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


@router.post("/businesses", response_model=BusinessResponse, status_code=201)
async def create_business(
    payload: BusinessCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Create a new tenant Business, default Branch, and BusinessOwner from the SaaS Admin dashboard."""
    email_clean = payload.email.strip().lower()
    if not email_clean or not payload.password or not payload.business_name.strip():
        raise HTTPException(status_code=400, detail="Business name, owner email, and password are required")

    existing_owner = (
        await db.execute(select(BusinessOwner).where(BusinessOwner.email == email_clean))
    ).scalar_one_or_none()
    if existing_owner:
        raise HTTPException(status_code=400, detail="Email is already registered")

    selected_plan = None
    if payload.plan_id:
        try:
            selected_plan = (
                await db.execute(select(Plan).where(Plan.id == UUID(payload.plan_id)))
            ).scalar_one_or_none()
        except ValueError:
            selected_plan = None
    if not selected_plan and payload.plan:
        selected_plan = (
            await db.execute(select(Plan).where(Plan.name == payload.plan))
        ).scalar_one_or_none()
    if not selected_plan:
        selected_plan = (
            await db.execute(select(Plan).where(Plan.is_active == True).order_by(Plan.price.asc()))
        ).scalars().first()

    req_status = (payload.status or "trial").strip().lower()
    if req_status not in {"trial", "active"}:
        req_status = "trial"

    trial_days = (
        int(payload.trial_days)
        if payload.trial_days is not None
        else (int(getattr(selected_plan, "trial_days", 14) or 14) if selected_plan else 14)
    )
    trial_ends = (
        datetime.now(timezone.utc) + timedelta(days=trial_days)
        if req_status == "trial" and trial_days > 0
        else None
    )

    business = Business(
        name=payload.business_name.strip(),
        plan_id=selected_plan.id if selected_plan else None,
        subscription_status=req_status,
        trial_ends_at=trial_ends,
        trial_features_override=payload.trial_features_override or {},
        custom_domain=payload.custom_domain.strip().lower() if payload.custom_domain and payload.custom_domain.strip() else None,
        category=payload.category.strip() if payload.category and payload.category.strip() else None,
        is_active=True,
    )
    db.add(business)
    await db.flush()

    default_branch = Branch(
        business_id=business.id,
        name=f"{business.name} - Main Branch",
        timezone="Asia/Baku",
        is_active=True,
    )
    db.add(default_branch)

    owner = BusinessOwner(
        business_id=business.id,
        name=(payload.owner_name or payload.business_name).strip(),
        phone=payload.phone.strip() if payload.phone and payload.phone.strip() else None,
        email=email_clean,
        password_hash=hash_password(payload.password),
        is_active=True,
    )
    db.add(owner)
    await db.flush()

    stmt = (
        select(Business)
        .where(Business.id == business.id)
        .options(
            selectinload(Business.owners),
            selectinload(Business.plan),
            selectinload(Business.branches),
        )
    )
    created_biz = (await db.execute(stmt)).scalar_one()
    return _biz_to_response(created_biz)


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
    """Approve, suspend, configure dynamic free trial duration/features, or assign white-label domain to a business."""
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
    if status_update.trial_days is not None:
        if status_update.trial_days > 0:
            biz.subscription_status = "trial"
            biz.is_active = True
            biz.trial_ends_at = datetime.now(timezone.utc) + timedelta(days=int(status_update.trial_days))
        else:
            biz.trial_ends_at = None
    if status_update.trial_features_override is not None:
        biz.trial_features_override = status_update.trial_features_override
        flag_modified(biz, "trial_features_override")
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
    """Create a new subscription plan with all entitlement and trial flags."""
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
    """Update a subscription plan and its dynamic free trial configuration."""
    plan = (await db.execute(select(Plan).where(Plan.id == UUID(id)))).scalar_one_or_none()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    updates = plan_in.model_dump(exclude_unset=True)
    msg_limit = updates.pop("message_limit", None)
    if msg_limit is not None:
        updates["ai_message_quota"] = msg_limit
    for k, v in updates.items():
        setattr(plan, k, v)
        if k in {"trial_features", "features"}:
            flag_modified(plan, k)
    await db.flush()
    return _plan_to_response(plan)


@router.get("/subscriptions")
async def list_subscriptions(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """List all business subscriptions with live message usage and trial status."""
    stmt = (
        select(Business)
        .options(selectinload(Business.plan))
        .order_by(Business.created_at.desc())
    )
    businesses = (await db.execute(stmt)).scalars().all()
    msg_counts_rows = (
        await db.execute(
            select(Conversation.business_id, func.count(Message.id))
            .join(Message, Message.conversation_id == Conversation.id)
            .group_by(Conversation.business_id)
        )
    ).all()
    msg_map = {row[0]: int(row[1] or 0) for row in msg_counts_rows}

    return [
        {
            "id": str(b.id),
            "business": b.name,
            "plan": b.plan.name if b.plan else "Starter",
            "status": b.subscription_status if b.is_active else "suspended",
            "trial_days_remaining": _calc_trial_days_remaining(b),
            "period": f"Trial ({_calc_trial_days_remaining(b)}d left)" if b.subscription_status == "trial" else "Monthly",
            "messagesUsed": f"{msg_map.get(b.id, 0)} / {b.plan.ai_message_quota if b.plan else 1000}",
        }
        for b in businesses
    ]


@router.get("/analytics", response_model=AnalyticsResponse)
async def get_platform_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    """Get precise platform-wide analytics and per-business AI spend from PostgreSQL."""
    stmt = (
        select(Business)
        .options(selectinload(Business.owners), selectinload(Business.plan))
        .order_by(Business.created_at.desc())
    )
    businesses = (await db.execute(stmt)).scalars().all()

    total_businesses = len(businesses)
    active_subscriptions = sum(1 for b in businesses if b.is_active and b.subscription_status != "suspended")
    trial_businesses = sum(1 for b in businesses if b.is_active and b.subscription_status == "trial")
    suspended_businesses = sum(1 for b in businesses if not b.is_active or b.subscription_status == "suspended")

    # Appointments breakdown
    appt_rows = (
        await db.execute(select(Appointment.business_id, Appointment.status, func.count(Appointment.id)).group_by(Appointment.business_id, Appointment.status))
    ).all()
    appt_by_biz: dict[UUID, int] = {}
    total_appointments = 0
    completed_appointments = 0
    cancelled_appointments = 0
    pending_appointments = 0
    for biz_id, st, cnt in appt_rows:
        c = int(cnt or 0)
        total_appointments += c
        appt_by_biz[biz_id] = appt_by_biz.get(biz_id, 0) + c
        st_val = st.value if hasattr(st, "value") else str(st)
        if st_val == "completed":
            completed_appointments += c
        elif st_val in {"cancelled", "no_show"}:
            cancelled_appointments += c
        else:
            pending_appointments += c

    # Payments / Settled Revenue breakdown
    pay_rows = (
        await db.execute(
            select(Payment.business_id, func.coalesce(func.sum(Payment.amount), 0))
            .where(Payment.status == PaymentStatus.completed)
            .group_by(Payment.business_id)
        )
    ).all()
    rev_by_biz = {r[0]: float(r[1] or 0.0) for r in pay_rows}
    total_settled_revenue_azn = round(sum(rev_by_biz.values()), 2)

    # Customers & Resellers count
    total_customers = int((await db.execute(select(func.count(Customer.id)))).scalar_one() or 0)
    total_resellers = int((await db.execute(select(func.count(Reseller.id)))).scalar_one() or 0)

    # Messages & Precise AI Token / Spend per Business
    msg_rows = (
        await db.execute(
            select(Conversation.business_id, Message.direction, Message.content)
            .join(Conversation, Message.conversation_id == Conversation.id)
        )
    ).all()

    biz_msg_stats: dict[UUID, dict[str, int]] = {}
    total_messages = 0
    inbound_messages = 0
    outbound_ai_messages = 0

    for biz_id, direction, content in msg_rows:
        if biz_id not in biz_msg_stats:
            biz_msg_stats[biz_id] = {"total": 0, "inbound": 0, "outbound": 0, "tokens": 0}
        stats = biz_msg_stats[biz_id]
        stats["total"] += 1
        total_messages += 1
        dir_val = direction.value if hasattr(direction, "value") else str(direction)
        # Estimate tokens: ~1 token per 3.5 chars + 350 system/context tokens per turn
        est_tokens = max(120, int(len(content or "") / 3.5)) + 350
        stats["tokens"] += est_tokens
        if dir_val == "inbound":
            stats["inbound"] += 1
            inbound_messages += 1
        else:
            stats["outbound"] += 1
            outbound_ai_messages += 1

    ai_spend_per_business: List[BusinessAISpendItem] = []
    total_ai_tokens_used = 0
    total_ai_spend_usd = 0.0
    total_ai_spend_azn = 0.0
    mrr_azn = 0.0

    for b in businesses:
        plan_name = b.plan.name if b.plan else "Starter"
        plan_price = float(b.plan.price) if b.plan else 29.0
        if b.is_active and b.subscription_status != "suspended":
            mrr_azn += plan_price

        assigned_model = (
            (b.plan.features or {}).get("assigned_model")
            if b.plan and isinstance(b.plan.features, dict)
            else None
        ) or "gemini-3.5-flash"
        cost_rate = MODEL_COST_PER_1M_TOKENS_USD.get(assigned_model, 0.75)

        m_stats = biz_msg_stats.get(b.id, {"total": 0, "inbound": 0, "outbound": 0, "tokens": 0})
        tokens = m_stats["tokens"]
        spend_usd = round((tokens / 1_000_000.0) * cost_rate, 4)
        spend_azn = round(spend_usd * USD_TO_AZN_RATE, 4)
        net_margin = round(plan_price - spend_azn, 2)

        total_ai_tokens_used += tokens
        total_ai_spend_usd += spend_usd
        total_ai_spend_azn += spend_azn

        owner_email = b.owners[0].email if getattr(b, "owners", None) else "—"
        ai_spend_per_business.append(
            BusinessAISpendItem(
                business_id=str(b.id),
                business_name=b.name,
                owner_email=owner_email,
                plan_name=plan_name,
                assigned_model=assigned_model,
                status=b.subscription_status if b.is_active else "suspended",
                trial_days_remaining=_calc_trial_days_remaining(b),
                total_messages=m_stats["total"],
                inbound_messages=m_stats["inbound"],
                ai_replies=m_stats["outbound"],
                tokens_used=tokens,
                ai_spend_usd=spend_usd,
                ai_spend_azn=spend_azn,
                appointments_count=appt_by_biz.get(b.id, 0),
                revenue_azn=round(rev_by_biz.get(b.id, 0.0), 2),
                plan_price_azn=plan_price,
                net_margin_azn=net_margin,
            )
        )

    mrr_azn = round(mrr_azn, 2)
    arr_azn = round(mrr_azn * 12, 2)
    total_ai_spend_usd = round(total_ai_spend_usd, 4)
    total_ai_spend_azn = round(total_ai_spend_azn, 4)
    net_platform_margin_azn = round(mrr_azn - total_ai_spend_azn, 2)

    return AnalyticsResponse(
        total_businesses=total_businesses,
        active_subscriptions=active_subscriptions,
        trial_businesses=trial_businesses,
        suspended_businesses=suspended_businesses,
        mrr_usd=mrr_azn,
        mrr_azn=mrr_azn,
        arr_azn=arr_azn,
        total_settled_revenue_azn=total_settled_revenue_azn,
        total_appointments=total_appointments,
        completed_appointments=completed_appointments,
        cancelled_appointments=cancelled_appointments,
        pending_appointments=pending_appointments,
        total_customers=total_customers,
        total_messages=total_messages,
        inbound_messages=inbound_messages,
        outbound_ai_messages=outbound_ai_messages,
        total_messages_this_month=total_messages,
        total_resellers=total_resellers,
        total_ai_tokens_used=total_ai_tokens_used,
        total_ai_spend_usd=total_ai_spend_usd,
        total_ai_spend_azn=total_ai_spend_azn,
        net_platform_margin_azn=net_platform_margin_azn,
        ai_spend_per_business=ai_spend_per_business,
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


# ----------------------------------------------------------------------
# Suby.fi v3-beta Full API Admin Endpoints (Products, Checkouts,
# Subscriptions, Customers, Payments, Off-Session, Refunds, Webhooks)
# ----------------------------------------------------------------------
@router.get("/suby/products")
async def suby_list_products(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    limit: int = 50,
    offset: int = 0,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_products(limit=limit, offset=offset)


@router.post("/suby/products")
async def suby_create_product(
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().create_product(
        name=payload["name"],
        price=payload["price"],
        currency=payload.get("currency", "USD"),
        description=payload.get("description"),
        recurring_interval=payload.get("recurringInterval") or payload.get("recurring_interval"),
        metadata=payload.get("metadata"),
    )


@router.patch("/suby/products/{product_id}")
async def suby_update_product(
    product_id: str,
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().update_product(product_id, payload)


@router.delete("/suby/products/{product_id}")
async def suby_delete_product(
    product_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().delete_product(product_id)


@router.get("/suby/checkout/sessions")
async def suby_list_checkout_sessions(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    limit: int = 50,
    offset: int = 0,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_checkout_sessions(limit=limit, offset=offset)


@router.get("/suby/checkout/sessions/{session_id}")
async def suby_get_checkout_session(
    session_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().get_checkout_session(session_id)


@router.post("/suby/checkout/sessions/{session_id}/cancel")
async def suby_cancel_checkout_session(
    session_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().cancel_checkout_session(session_id)


@router.get("/suby/subscriptions")
async def suby_list_subscriptions(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    customer_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_subscriptions(customer_id=customer_id, status=status, limit=limit, offset=offset)


@router.get("/suby/subscriptions/{subscription_id}")
async def suby_get_subscription(
    subscription_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().get_subscription(subscription_id)


@router.patch("/suby/subscriptions/{subscription_id}")
async def suby_update_subscription(
    subscription_id: str,
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().update_subscription(subscription_id, payload)


@router.post("/suby/subscriptions/{subscription_id}/cancel")
async def suby_cancel_subscription(
    subscription_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    cancel_at_period_end: bool = False,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().cancel_subscription(subscription_id, cancel_at_period_end=cancel_at_period_end)


@router.post("/suby/subscriptions/{subscription_id}/pause")
async def suby_pause_subscription(
    subscription_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().pause_subscription(subscription_id)


@router.post("/suby/subscriptions/{subscription_id}/resume")
async def suby_resume_subscription(
    subscription_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().resume_subscription(subscription_id)


@router.get("/suby/customers")
async def suby_list_customers(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    limit: int = 50,
    offset: int = 0,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_customers(limit=limit, offset=offset)


@router.post("/suby/customers")
async def suby_create_customer(
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().create_customer(
        email=payload["email"],
        name=payload.get("name"),
        phone=payload.get("phone"),
        metadata=payload.get("metadata"),
    )


@router.get("/suby/customers/{customer_id}/payment-methods")
async def suby_list_customer_payment_methods(
    customer_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_customer_payment_methods(customer_id)


@router.get("/suby/payments")
async def suby_list_payments(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    limit: int = 50,
    offset: int = 0,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_payments(limit=limit, offset=offset)


@router.post("/suby/payments/off-session")
async def suby_create_off_session_payment(
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().create_off_session_payment(
        customer_id=payload["customerId"],
        payment_method_id=payload["paymentMethodId"],
        amount=payload["amount"],
        currency=payload.get("currency", "USD"),
        description=payload.get("description"),
        metadata=payload.get("metadata"),
    )


@router.get("/suby/refunds")
async def suby_list_refunds(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
    limit: int = 50,
    offset: int = 0,
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_refunds(limit=limit, offset=offset)


@router.post("/suby/refunds")
async def suby_create_refund(
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().create_refund(
        payment_id=payload["paymentId"],
        amount=payload.get("amount"),
        reason=payload.get("reason"),
    )


@router.get("/suby/webhooks")
async def suby_list_webhooks(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().list_webhooks()


@router.post("/suby/webhooks")
async def suby_create_webhook(
    payload: dict[str, Any],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().create_webhook(
        url=payload.get("url") or f"https://api.{settings.PLATFORM_DOMAIN}/api/v1/webhooks/payments/suby",
        events=payload.get("events"),
    )


@router.delete("/suby/webhooks/{webhook_id}")
async def suby_delete_webhook(
    webhook_id: str,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))],
):
    from app.integrations.payments.suby import SubyAdapter
    return await SubyAdapter().delete_webhook(webhook_id)
