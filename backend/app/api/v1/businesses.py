from datetime import datetime, timezone
import httpx
from typing import Annotated, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.orm.attributes import flag_modified
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_role, get_business_context
from app.models.business import Business, Branch
from app.models.appointment import Appointment
from app.models.conversation import Conversation, Message
from app.models.payment import Payment, PaymentGatewayConfig
from app.services.custom_domain_service import CustomDomainService
from app.integrations.whatsapp.client import EvolutionAPIClient

router = APIRouter()


class BusinessResponse(BaseModel):
    id: str
    name: str
    custom_domain: Optional[str] = None
    reseller_id: Optional[str] = None
    plan_name: str = "Starter"
    subscription_status: str = "trial"
    trial_ends_at: Optional[str] = None
    trial_days_remaining: int = 0
    entitlements: dict = {}
    webhook_urls: dict = {}
    settings: dict = {}


class BusinessUpdate(BaseModel):
    name: str | None = None
    custom_domain: str | None = None
    settings: dict | None = None


class BusinessAnalyticsResponse(BaseModel):
    appointments_this_month: int
    revenue_this_month: float
    total_messages: int = 0
    ai_tokens_used: int = 0
    ai_spend_usd: float = 0.0
    ai_spend_azn: float = 0.0


class CustomDomainVerifyRequest(BaseModel):
    custom_domain: str


class TelegramConnectRequest(BaseModel):
    bot_token: str


class InstagramConnectRequest(BaseModel):
    instagram_page_id: str
    instagram_access_token: str
    instagram_verify_token: Optional[str] = "randevu_ig_verify"


def _parse_uuid_safe(val: str) -> Optional[UUID]:
    try:
        return UUID(str(val))
    except (ValueError, TypeError):
        return None


def _build_business_response(biz: Business) -> BusinessResponse:
    plan = getattr(biz, "plan", None)
    entitlements = {
        "allows_whatsapp": bool(getattr(plan, "allows_whatsapp", True)) if plan else True,
        "allows_instagram": bool(
            getattr(plan, "allows_instagram", False) or getattr(plan, "allows_omnichannel_messaging", False)
        )
        if plan
        else False,
        "allows_telegram": bool(
            getattr(plan, "allows_telegram", False) or getattr(plan, "allows_omnichannel_messaging", False)
        )
        if plan
        else False,
        "allows_online_payments": bool(getattr(plan, "allows_online_payments", True)) if plan else True,
        "allows_no_show_deposits": bool(getattr(plan, "allows_no_show_deposits", False)) if plan else False,
        "allows_gcal_sync": bool(getattr(plan, "allows_gcal_sync", False)) if plan else False,
        "allows_apple_cal_sync": bool(getattr(plan, "allows_apple_cal_sync", False)) if plan else False,
        "allows_custom_domain": bool(getattr(plan, "allows_custom_domain", False)) if plan else False,
    }
    now_utc = datetime.now(timezone.utc)
    trial_days_remaining = 0
    if biz.trial_ends_at:
        end_dt = biz.trial_ends_at if biz.trial_ends_at.tzinfo else biz.trial_ends_at.replace(tzinfo=timezone.utc)
        trial_days_remaining = max(0, (end_dt - now_utc).days)

    if biz.subscription_status == "trial" and (not biz.trial_ends_at or trial_days_remaining > 0):
        plan_trial_feats = getattr(plan, "trial_features", None) if plan else None
        if isinstance(plan_trial_feats, dict):
            for k, v in plan_trial_feats.items():
                if isinstance(v, bool):
                    entitlements[k] = v
        if isinstance(biz.trial_features_override, dict):
            for k, v in biz.trial_features_override.items():
                if isinstance(v, bool):
                    entitlements[k] = v

    api_base = f"https://api.{settings.PLATFORM_DOMAIN}/api/v1/webhooks"
    webhook_urls = {
        "whatsapp": f"{api_base}/whatsapp",
        "instagram": f"{api_base}/instagram",
        "telegram": f"{api_base}/telegram/{biz.id}",
    }
    return BusinessResponse(
        id=str(biz.id),
        name=biz.name,
        custom_domain=biz.custom_domain,
        reseller_id=str(biz.reseller_id) if biz.reseller_id else None,
        plan_name=plan.name if plan else "Starter",
        subscription_status=biz.subscription_status or "trial",
        trial_ends_at=biz.trial_ends_at.strftime("%Y-%m-%d") if biz.trial_ends_at else None,
        trial_days_remaining=trial_days_remaining,
        entitlements=entitlements,
        webhook_urls=webhook_urls,
        settings=biz.default_ai_tone_config or {},
    )


async def _sync_gateway_configs(db: AsyncSession, biz_uuid: UUID, cfg: dict[str, Any]) -> None:
    """Sync Payriff and Paymegate credentials into PaymentGatewayConfig table and register Paymegate webhook."""
    from app.integrations.payments.paymegate import PaymegateAdapter

    payriff_mid = (cfg.get("payriff_merchant_id") or "").strip()
    payriff_sec = (cfg.get("payriff_secret_key") or "").strip()
    if payriff_mid:
        existing_pr = (
            await db.execute(
                select(PaymentGatewayConfig).where(
                    PaymentGatewayConfig.business_id == biz_uuid,
                    PaymentGatewayConfig.provider == "payriff",
                )
            )
        ).scalar_one_or_none()
        creds = {"merchant_id": payriff_mid, "secret_key": payriff_sec}
        if existing_pr:
            existing_pr.merchant_credentials = creds
            existing_pr.is_active = True
        else:
            db.add(
                PaymentGatewayConfig(
                    business_id=biz_uuid,
                    provider="payriff",
                    merchant_credentials=creds,
                    is_active=True,
                )
            )

    pmg_key = (cfg.get("paymegate_api_key") or cfg.get("paymengate_api_key") or "").strip()
    pmg_sec = (cfg.get("paymegate_webhook_secret") or cfg.get("paymengate_secret_key") or "").strip()
    if pmg_key:
        existing_pmg = (
            await db.execute(
                select(PaymentGatewayConfig).where(
                    PaymentGatewayConfig.business_id == biz_uuid,
                    PaymentGatewayConfig.provider == "paymegate",
                )
            )
        ).scalar_one_or_none()
        creds = {"api_key": pmg_key, "webhook_secret": pmg_sec}
        if existing_pmg:
            existing_pmg.merchant_credentials = creds
            existing_pmg.is_active = True
        else:
            db.add(
                PaymentGatewayConfig(
                    business_id=biz_uuid,
                    provider="paymegate",
                    merchant_credentials=creds,
                    is_active=True,
                )
            )
        try:
            webhook_url = f"https://api.{settings.PLATFORM_DOMAIN}/api/v1/webhooks/payments/paymegate/{biz_uuid}"
            await PaymegateAdapter().register_webhook(api_key=pmg_key, webhook_url=webhook_url)
        except Exception:
            pass


@router.get("/", response_model=BusinessResponse)
async def get_own_business(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get details of the currently authenticated business."""
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        stmt = select(Business).where(Business.id == biz_uuid).options(selectinload(Business.plan))
        biz = (await db.execute(stmt)).scalar_one_or_none()
        if biz:
            return _build_business_response(biz)
    return BusinessResponse(id=business_id, name="My Business")


@router.put("/", response_model=BusinessResponse)
async def update_own_business(
    update_data: BusinessUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update settings of the currently authenticated business."""
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        stmt = select(Business).where(Business.id == biz_uuid).options(selectinload(Business.plan))
        biz = (await db.execute(stmt)).scalar_one_or_none()
        if biz:
            if update_data.name is not None:
                biz.name = update_data.name
            if update_data.custom_domain is not None:
                biz.custom_domain = update_data.custom_domain.strip().lower() or None
            if update_data.settings is not None:
                merged_settings = dict(biz.default_ai_tone_config or {})
                merged_settings.update(update_data.settings)
                biz.default_ai_tone_config = merged_settings
                flag_modified(biz, "default_ai_tone_config")
                await _sync_gateway_configs(db, biz_uuid, merged_settings)
            await db.flush()
            return _build_business_response(biz)
    return BusinessResponse(
        id=business_id,
        name=update_data.name or "My Business",
        custom_domain=update_data.custom_domain,
        settings=update_data.settings or {},
    )


@router.post("/telegram/connect")
async def connect_telegram_bot(
    req: TelegramConnectRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Validate Telegram Bot Token via BotFather API and automatically register the webhook."""
    biz_uuid = _parse_uuid_safe(business_id)
    if not biz_uuid:
        raise HTTPException(status_code=400, detail="Invalid business context")

    stmt = select(Business).where(Business.id == biz_uuid).options(selectinload(Business.plan))
    biz = (await db.execute(stmt)).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    token = req.bot_token.strip()
    if ":" not in token:
        raise HTTPException(status_code=400, detail="Invalid Telegram Bot Token format (expected 123456:ABC-DEF...)")

    webhook_url = f"https://api.{settings.PLATFORM_DOMAIN}/api/v1/webhooks/telegram/{biz.id}"
    bot_username = ""
    bot_name = ""
    webhook_registered = False

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            me_resp = await client.get(f"https://api.telegram.org/bot{token}/getMe")
            me_data = me_resp.json()
            if not me_data.get("ok"):
                raise HTTPException(
                    status_code=400,
                    detail=me_data.get("description", "Telegram rejected the Bot Token."),
                )
            bot_info = me_data.get("result", {})
            bot_username = bot_info.get("username", "")
            bot_name = bot_info.get("first_name", "")

            wh_resp = await client.post(
                f"https://api.telegram.org/bot{token}/setWebhook",
                json={"url": webhook_url, "allowed_updates": ["message", "edited_message"]},
            )
            wh_data = wh_resp.json()
            webhook_registered = bool(wh_data.get("ok"))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Could not reach Telegram API: {exc}")

    cfg = dict(biz.default_ai_tone_config or {})
    cfg["telegram_bot_token"] = token
    cfg["telegram_bot_username"] = bot_username
    cfg["telegram_bot_name"] = bot_name
    cfg["telegram_connected"] = True
    cfg["telegram_webhook_url"] = webhook_url
    biz.default_ai_tone_config = cfg
    flag_modified(biz, "default_ai_tone_config")
    await db.flush()

    return {
        "status": "connected",
        "bot_username": bot_username,
        "bot_name": bot_name,
        "webhook_url": webhook_url,
        "webhook_registered": webhook_registered,
    }


@router.post("/instagram/connect")
async def connect_instagram_account(
    req: InstagramConnectRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Save Instagram Business Account / Page ID and Meta Access Token for Instagram Direct AI."""
    biz_uuid = _parse_uuid_safe(business_id)
    if not biz_uuid:
        raise HTTPException(status_code=400, detail="Invalid business context")

    biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    webhook_url = f"https://api.{settings.PLATFORM_DOMAIN}/api/v1/webhooks/instagram"
    cfg = dict(biz.default_ai_tone_config or {})
    cfg["instagram_page_id"] = req.instagram_page_id.strip()
    cfg["instagram_access_token"] = req.instagram_access_token.strip()
    cfg["instagram_verify_token"] = (req.instagram_verify_token or "randevu_ig_verify").strip()
    cfg["instagram_connected"] = bool(cfg["instagram_page_id"] and cfg["instagram_access_token"])
    cfg["instagram_webhook_url"] = webhook_url
    biz.default_ai_tone_config = cfg
    flag_modified(biz, "default_ai_tone_config")
    await db.flush()

    return {
        "status": "connected" if cfg["instagram_connected"] else "incomplete",
        "instagram_page_id": cfg["instagram_page_id"],
        "webhook_url": webhook_url,
        "verify_token": cfg["instagram_verify_token"],
    }


@router.get("/analytics", response_model=BusinessAnalyticsResponse)
async def get_business_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get analytics and AI spend for the current business."""
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        appt_count = (
            await db.execute(select(func.count(Appointment.id)).where(Appointment.business_id == biz_uuid))
        ).scalar_one()
        rev_sum = (
            await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.business_id == biz_uuid))
        ).scalar_one()
        msg_rows = (
            await db.execute(
                select(Message.content, Message.direction)
                .join(Conversation, Message.conversation_id == Conversation.id)
                .where(Conversation.business_id == biz_uuid)
            )
        ).all()
        total_msgs = len(msg_rows)
        tokens_used = sum(max(120, int(len(r[0] or "") / 3.5)) + 350 for r in msg_rows)
        spend_usd = round((tokens_used / 1_000_000.0) * 0.75, 4)
        spend_azn = round(spend_usd * 1.70, 4)
        return BusinessAnalyticsResponse(
            appointments_this_month=int(appt_count or 0),
            revenue_this_month=float(rev_sum or 0.0),
            total_messages=total_msgs,
            ai_tokens_used=tokens_used,
            ai_spend_usd=spend_usd,
            ai_spend_azn=spend_azn,
        )
    return BusinessAnalyticsResponse(appointments_this_month=0, revenue_this_month=0.0)


@router.post("/custom-domain/verify")
async def verify_business_custom_domain(
    req: CustomDomainVerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Verify CNAME pointing to cname.randevu.vip and provision SSL."""
    biz_uuid = _parse_uuid_safe(business_id) or UUID("00000000-0000-0000-0000-000000000001")
    service = CustomDomainService()
    status_res = await service.verify_and_provision_cname(req.custom_domain, biz_uuid)
    if _parse_uuid_safe(business_id):
        biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
        if biz:
            biz.custom_domain = status_res.custom_domain
            await db.flush()
    return status_res.__dict__


@router.get("/whatsapp/qr-code")
async def get_whatsapp_pairing_qr(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
    branch_id: Optional[str] = None,
):
    """Proxy WhatsApp QR code generation and status from internal Evolution API container."""
    instance_name = f"randevu_{business_id[:8]}_{branch_id[:8] if branch_id else 'main'}"
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        branch = (await db.execute(select(Branch).where(Branch.business_id == biz_uuid))).scalars().first()
        if branch and not branch.whatsapp_instance_id:
            branch.whatsapp_instance_id = instance_name
            await db.flush()

    evo_client = EvolutionAPIClient(
        base_url=settings.EVOLUTION_API_URL,
        api_key=settings.EVOLUTION_API_KEY,
    )
    try:
        try:
            state_res = await evo_client.get_instance_status(instance_name)
            conn_state = (
                state_res.get("instance", {}).get("state")
                or state_res.get("state")
                or ""
            )
            if conn_state == "open":
                await evo_client.close()
                return {
                    "instance_name": instance_name,
                    "status": "connected",
                    "qr_code_data_url": None,
                    "source": "evolution_api_internal",
                }
        except Exception:
            await evo_client.create_instance(
                instance_name,
                webhook_url="http://backend:22800/api/v1/webhooks/whatsapp",
            )

        connect_res = await evo_client.connect_instance(instance_name)
        await evo_client.close()
        qr_base64 = connect_res.get("base64") or connect_res.get("qrcode", {}).get("base64")
        if qr_base64:
            return {
                "instance_name": instance_name,
                "status": "pairing",
                "qr_code_data_url": qr_base64,
                "source": "evolution_api_internal",
            }
        return {
            "instance_name": instance_name,
            "status": connect_res.get("instance", {}).get("state", "initializing"),
            "qr_code_data_url": None,
            "source": "evolution_api_internal",
        }
    except Exception as exc:
        await evo_client.close()
        return {
            "instance_name": instance_name,
            "status": "unavailable",
            "qr_code_data_url": None,
            "detail": str(exc),
            "source": "evolution_api_internal",
        }


class SubscriptionCheckoutRequest(BaseModel):
    plan_id: str | None = None
    plan_name: str | None = None


@router.get("/subscription")
async def get_business_subscription(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Return current subscription plan, status, trial expiry, and available upgrade plans."""
    biz = (await db.execute(select(Business).where(Business.id == UUID(business_id)))).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    plans = (await db.execute(select(Plan).where(Plan.is_active.is_(True)).order_by(Plan.price.asc()))).scalars().all()
    current_plan = next((p for p in plans if p.id == biz.plan_id), None)
    return {
        "current_plan_id": str(biz.plan_id) if biz.plan_id else None,
        "current_plan_name": current_plan.name if current_plan else "Starter",
        "current_plan_price": float(current_plan.price) if current_plan else 29.0,
        "subscription_status": biz.subscription_status or "trial",
        "trial_ends_at": biz.trial_ends_at.isoformat() if biz.trial_ends_at else None,
        "plans": [
            {
                "id": str(p.id),
                "name": p.name,
                "price": float(p.price),
                "ai_message_quota": int(p.ai_message_quota or 1000),
            }
            for p in plans
        ],
    }


@router.post("/subscription/checkout")
async def create_subscription_checkout(
    req: SubscriptionCheckoutRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create a live Paymegate/Payriff checkout link for SaaS plan payment or upgrade."""
    from decimal import Decimal
    from app.integrations.payments.paymegate import PaymegateAdapter
    from app.integrations.payments.payriff import PayriffAdapter

    biz = (await db.execute(select(Business).where(Business.id == UUID(business_id)))).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    target_plan = None
    if req.plan_id:
        try:
            target_plan = (await db.execute(select(Plan).where(Plan.id == UUID(req.plan_id)))).scalar_one_or_none()
        except ValueError:
            target_plan = None
    if not target_plan and req.plan_name:
        target_plan = (await db.execute(select(Plan).where(Plan.name == req.plan_name))).scalar_one_or_none()
    if not target_plan and biz.plan_id:
        target_plan = (await db.execute(select(Plan).where(Plan.id == biz.plan_id))).scalar_one_or_none()
    if not target_plan:
        raise HTTPException(status_code=404, detail="Subscription plan not found")

    amount = Decimal(str(target_plan.price))
    sub_payment = Payment(
        business_id=biz.id,
        appointment_id=None,
        amount=float(amount),
        currency="AZN",
        method=PaymentMethod.paymegate if settings.PAYMEGATE_API_KEY else PaymentMethod.payriff,
        status=PaymentStatus.pending,
        notes=f"SaaS Subscription - {target_plan.name}",
    )
    db.add(sub_payment)
    await db.flush()

    checkout_url: str | None = None
    if settings.PAYMEGATE_API_KEY:
        link_res = await PaymegateAdapter().create_payment_link(
            payment_id=sub_payment.id,
            amount=amount,
            currency="AZN",
            description=f"Randevu.vip {target_plan.name} Subscription",
            merchant_config={
                "business_id": str(biz.id),
                "type": "saas_subscription",
                "plan_id": str(target_plan.id),
            },
            return_url=f"https://app.{settings.PLATFORM_DOMAIN}/payments",
        )
        sub_payment.gateway_transaction_id = link_res.transaction_id
        checkout_url = link_res.payment_url
    elif settings.PAYRIFF_SECRET_KEY:
        link_res = await PayriffAdapter().create_payment_link(
            payment_id=sub_payment.id,
            amount=amount,
            currency="AZN",
            description=f"Randevu.vip {target_plan.name} Subscription",
            merchant_config={},
            return_url=f"https://app.{settings.PLATFORM_DOMAIN}/payments",
        )
        sub_payment.gateway_transaction_id = link_res.transaction_id
        checkout_url = link_res.payment_url

    await db.commit()
    return {
        "payment_id": str(sub_payment.id),
        "plan_name": target_plan.name,
        "amount": float(amount),
        "currency": "AZN",
        "checkout_url": checkout_url,
    }


@router.get("/public/discover")
async def discover_public_businesses(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: Optional[str] = None,
    q: Optional[str] = None,
):
    """Public discovery endpoint for Customer Mobile App & Web Directory."""
    stmt = (
        select(Business)
        .options(selectinload(Business.branches), selectinload(Business.services))
        .where(Business.is_active.is_(True))
        .order_by(Business.created_at.desc())
        .limit(50)
    )
    if category and category.lower() != "all":
        stmt = stmt.where(Business.category.ilike(f"%{category.strip()}%"))
    if q and q.strip():
        stmt = stmt.where(Business.name.ilike(f"%{q.strip()}%"))

    rows = (await db.execute(stmt)).scalars().all()
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "category": b.category or "Service Business",
            "address": b.branches[0].address if getattr(b, "branches", None) and b.branches[0].address else "Baku",
            "branches_count": len(b.branches) if getattr(b, "branches", None) else 0,
            "services_count": len([s for s in (b.services or []) if s.is_active]),
        }
        for b in rows
    ]


@router.get("/public/resolve")
async def resolve_public_booking_business(
    db: Annotated[AsyncSession, Depends(get_db)],
    domain: Optional[str] = None,
    business_id: Optional[str] = None,
):
    """Public endpoint to load business services and staff for white-label custom domains or /book/:businessId."""
    from app.models.service import Service
    from app.models.staff import Staff

    biz = None
    if business_id:
        try:
            biz = (await db.execute(select(Business).where(Business.id == UUID(business_id), Business.is_active.is_(True)))).scalar_one_or_none()
        except ValueError:
            biz = None
    elif domain:
        clean_dom = domain.strip().lower()
        biz = (await db.execute(select(Business).where(Business.custom_domain == clean_dom, Business.is_active.is_(True)))).scalar_one_or_none()

    if not biz:
        raise HTTPException(status_code=404, detail="Business booking page not found")

    services = (
        await db.execute(select(Service).where(Service.business_id == biz.id, Service.is_active.is_(True)))
    ).scalars().all()
    staff = (
        await db.execute(select(Staff).where(Staff.business_id == biz.id, Staff.is_active.is_(True)))
    ).scalars().all()

    return {
        "id": str(biz.id),
        "name": biz.name,
        "category": biz.category,
        "services": [
            {
                "id": str(s.id),
                "name": s.name,
                "duration_minutes": s.duration_minutes,
                "price": float(s.price),
                "currency": s.currency or "AZN",
            }
            for s in services
        ],
        "staff": [
            {"id": str(st.id), "name": st.name, "role": st.role}
            for st in staff
        ],
    }


class PublicBookRequest(BaseModel):
    service_id: str
    staff_id: str
    date: str
    time: str
    customer_name: str
    customer_phone: str


@router.post("/public/{business_id}/book")
async def create_public_booking(
    business_id: str,
    req: PublicBookRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Create a real appointment from a public white-label booking page (with Beh deposit evaluation)."""
    from app.models.customer import Customer
    from app.integrations.ai.tool_executor import ToolExecutor

    biz = (await db.execute(select(Business).where(Business.id == UUID(business_id), Business.is_active.is_(True)))).scalar_one_or_none()
    if not biz:
        raise HTTPException(status_code=404, detail="Business not found")

    branch = (await db.execute(select(Branch).where(Branch.business_id == biz.id, Branch.is_active.is_(True)))).scalars().first()
    if not branch:
        raise HTTPException(status_code=400, detail="Business has no active branch")

    phone_clean = req.customer_phone.strip()
    customer = (
        await db.execute(select(Customer).where(Customer.business_id == biz.id, Customer.phone_number == phone_clean))
    ).scalar_one_or_none()
    if not customer:
        customer = Customer(
            business_id=biz.id,
            phone_number=phone_clean,
            name=req.customer_name.strip(),
            language_pref="az",
        )
        db.add(customer)
        await db.flush()

    executor = ToolExecutor(db=db, branch_id=branch.id, business_id=biz.id, customer_id=customer.id)
    return await executor._create_appointment(
        service_id=req.service_id,
        staff_id=req.staff_id,
        date=req.date,
        time=req.time,
        customer_name=req.customer_name.strip(),
    )
