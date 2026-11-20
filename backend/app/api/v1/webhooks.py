import logging
from datetime import datetime, timezone
from uuid import UUID
from fastapi import APIRouter, Request, Header, HTTPException, Depends, Query
from fastapi.responses import PlainTextResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.integrations.whatsapp.webhook_handler import WebhookHandler, ParsedWebhookMessage
from app.integrations.omnichannel.channel_handler import OmnichannelHandler
from app.services.guardrail_service import GuardrailService
from app.services.payment_service import PaymentService
from app.models.business import Business, Branch
from app.models.customer import Customer
from app.models.conversation import Conversation, Message, MessageDirection

logger = logging.getLogger(__name__)
router = APIRouter()
webhook_handler = WebhookHandler()
omnichannel_handler = OmnichannelHandler()
guardrail_service = GuardrailService()


async def _persist_incoming_message(
    db: AsyncSession,
    biz: Business,
    parsed: ParsedWebhookMessage,
    guardrail_out_of_scope: bool,
) -> Conversation | None:
    """Persist Customer, Conversation, and inbound Message for any channel (WhatsApp, Instagram, Telegram)."""
    if not parsed.sender_phone or parsed.is_group:
        return None

    branch = (await db.execute(select(Branch).where(Branch.business_id == biz.id))).scalars().first()
    if not branch:
        branch = Branch(business_id=biz.id, name="Main Branch", timezone="Asia/Baku", is_active=True)
        db.add(branch)
        await db.flush()

    cust = (
        await db.execute(
            select(Customer).where(
                Customer.business_id == biz.id,
                Customer.phone_number == parsed.sender_phone,
            )
        )
    ).scalar_one_or_none()
    if not cust:
        cust = Customer(
            business_id=biz.id,
            phone_number=parsed.sender_phone,
            name=parsed.sender_name or parsed.sender_phone,
        )
        db.add(cust)
        await db.flush()

    conv = (
        await db.execute(
            select(Conversation).where(
                Conversation.business_id == biz.id,
                Conversation.customer_id == cust.id,
            )
        )
    ).scalars().first()
    if not conv:
        conv = Conversation(
            business_id=biz.id,
            branch_id=branch.id,
            customer_id=cust.id,
            whatsapp_chat_jid=parsed.remote_jid,
            ai_active=True,
        )
        db.add(conv)
        await db.flush()

    if guardrail_out_of_scope:
        conv.ai_active = False

    conv.last_message_at = datetime.now(timezone.utc)
    if parsed.message_text:
        db.add(
            Message(
                conversation_id=conv.id,
                direction=MessageDirection.inbound,
                sender_role="customer",
                content=parsed.message_text,
                message_type=parsed.message_type or "text",
                whatsapp_message_id=parsed.message_id,
            )
        )
    await db.flush()
    return conv


@router.post("/whatsapp")
async def evolution_webhook(
    request: Request,
    apikey: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """Receive Evolution API WhatsApp webhooks."""
    if apikey and settings.EVOLUTION_API_KEY and apikey != settings.EVOLUTION_API_KEY:
        if settings.ENVIRONMENT == "prod":
            raise HTTPException(status_code=401, detail="Invalid Evolution API webhook key")

    payload = await request.json()
    parsed = webhook_handler.parse_message(payload)
    if not parsed or parsed.is_from_me:
        return {"status": "ignored"}

    guardrail_result = None
    if parsed.message_text:
        guardrail_result = guardrail_service.evaluate_message(
            message_text=parsed.message_text,
            language="az",
            is_solo_business=False,
        )

    try:
        biz = None
        if parsed.instance_name:
            branch_match = (
                await db.execute(select(Branch).where(Branch.whatsapp_instance_id == parsed.instance_name))
            ).scalar_one_or_none()
            if branch_match:
                biz = (
                    await db.execute(select(Business).where(Business.id == branch_match.business_id))
                ).scalar_one_or_none()
        if not biz:
            biz = (await db.execute(select(Business).where(Business.is_active == True))).scalars().first()

        if biz:
            await _persist_incoming_message(
                db=db,
                biz=biz,
                parsed=parsed,
                guardrail_out_of_scope=bool(guardrail_result and guardrail_result.is_out_of_scope),
            )
    except Exception as exc:
        logger.warning(f"WhatsApp webhook persistence skipped: {exc}")

    return {
        "status": "ok",
        "channel": "whatsapp",
        "instance": parsed.instance_name,
        "sender_phone": parsed.sender_phone,
        "is_group": parsed.is_group,
        "out_of_scope": guardrail_result.is_out_of_scope if guardrail_result else False,
    }


@router.get("/instagram")
async def verify_instagram_webhook(
    hub_mode: str | None = Query(default=None, alias="hub.mode"),
    hub_verify_token: str | None = Query(default=None, alias="hub.verify_token"),
    hub_challenge: str | None = Query(default=None, alias="hub.challenge"),
):
    """Meta Graph API Webhook Verification endpoint for Instagram Direct."""
    if hub_mode == "subscribe" and hub_challenge:
        return PlainTextResponse(content=str(hub_challenge), status_code=200)
    raise HTTPException(status_code=403, detail="Webhook verification failed")


@router.post("/instagram")
async def instagram_webhook(
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Receive Instagram Direct Messages from Meta Graph API."""
    payload = await request.json()
    parsed = omnichannel_handler.parse_meta_webhook(payload, channel="instagram")
    if not parsed:
        return {"status": "ignored", "channel": "instagram"}

    guardrail_result = None
    if parsed.message_text:
        guardrail_result = guardrail_service.evaluate_message(
            message_text=parsed.message_text,
            language="az",
            is_solo_business=False,
        )

    try:
        recipient_page_id = parsed.instance_name.replace("instagram_instance_", "")
        stmt = select(Business).where(Business.is_active == True).options(selectinload(Business.plan))
        businesses = (await db.execute(stmt)).scalars().all()
        matched_biz = None
        for b in businesses:
            cfg = b.default_ai_tone_config or {}
            if cfg.get("instagram_page_id") and str(cfg.get("instagram_page_id")) == recipient_page_id:
                matched_biz = b
                break
        if not matched_biz and businesses:
            matched_biz = businesses[0]

        if matched_biz:
            plan = matched_biz.plan
            ig_allowed = bool(
                not plan
                or getattr(plan, "allows_instagram", False)
                or getattr(plan, "allows_omnichannel_messaging", False)
            )
            if not ig_allowed:
                return {"status": "plan_disabled", "channel": "instagram"}

            await _persist_incoming_message(
                db=db,
                biz=matched_biz,
                parsed=parsed,
                guardrail_out_of_scope=bool(guardrail_result and guardrail_result.is_out_of_scope),
            )
    except Exception as exc:
        logger.warning(f"Instagram webhook persistence skipped: {exc}")

    return {"status": "ok", "channel": "instagram", "sender": parsed.sender_phone}


@router.post("/telegram/{business_id}")
@router.post("/telegram")
async def telegram_webhook(
    request: Request,
    business_id: str | None = None,
    db: AsyncSession = Depends(get_db),
):
    """Receive Telegram Bot updates for a specific business or default active business."""
    payload = await request.json()
    parsed = omnichannel_handler.parse_telegram_webhook(payload, business_id=business_id or "default")
    if not parsed:
        return {"status": "ignored", "channel": "telegram"}

    guardrail_result = None
    if parsed.message_text:
        guardrail_result = guardrail_service.evaluate_message(
            message_text=parsed.message_text,
            language="az",
            is_solo_business=False,
        )

    try:
        matched_biz = None
        if business_id:
            try:
                biz_uuid = UUID(str(business_id))
                stmt = select(Business).where(Business.id == biz_uuid).options(selectinload(Business.plan))
                matched_biz = (await db.execute(stmt)).scalar_one_or_none()
            except ValueError:
                matched_biz = None

        if not matched_biz:
            stmt = select(Business).where(Business.is_active == True).options(selectinload(Business.plan))
            matched_biz = (await db.execute(stmt)).scalars().first()

        if matched_biz:
            plan = matched_biz.plan
            tg_allowed = bool(
                not plan
                or getattr(plan, "allows_telegram", False)
                or getattr(plan, "allows_omnichannel_messaging", False)
            )
            if not tg_allowed:
                return {"status": "plan_disabled", "channel": "telegram"}

            conv = await _persist_incoming_message(
                db=db,
                biz=matched_biz,
                parsed=parsed,
                guardrail_out_of_scope=bool(guardrail_result and guardrail_result.is_out_of_scope),
            )
            cfg = matched_biz.default_ai_tone_config or {}
            bot_token = cfg.get("telegram_bot_token")
            if bot_token and conv and conv.ai_active and parsed.message_text:
                reply_text = (
                    f"Salam! {matched_biz.name} AI köməkçisinə xoş gəlmisiniz. "
                    f"Mesajınız qeydə alındı: '{parsed.message_text}'. Hansı xidmət və saat üçün randevu istərdiniz?"
                )
                sent = await omnichannel_handler.send_telegram_message(
                    bot_token=bot_token,
                    chat_id=parsed.sender_phone,
                    text=reply_text,
                )
                if sent:
                    db.add(
                        Message(
                            conversation_id=conv.id,
                            direction=MessageDirection.outbound,
                            sender_role="ai",
                            content=reply_text,
                            message_type="text",
                        )
                    )
                    await db.flush()
    except Exception as exc:
        logger.warning(f"Telegram webhook persistence skipped: {exc}")

    return {"status": "ok", "channel": "telegram", "sender": parsed.sender_phone}


@router.post("/payments/{provider}")
async def platform_payment_gateway_webhook(
    provider: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle platform-level payment gateway webhooks (Creem, Payriff, Paymegate) without business_id in URL."""
    import json
    from datetime import datetime, timedelta, timezone
    from app.models.payment import Payment, PaymentStatus
    from app.models.business import Business
    from app.models.subscription import Subscription, SubscriptionStatus
    from app.integrations.payments.creem import CreemAdapter
    from app.integrations.payments.paymegate import PaymegateAdapter

    raw_body = await request.body()
    payload = json.loads(raw_body.decode("utf-8")) if raw_body else {}
    headers = dict(request.headers)
    prov = provider.lower().strip()
    if prov == "paymengate":
        prov = "paymegate"

    obj = payload.get("object") if isinstance(payload.get("object"), dict) else {}
    metadata = (
        obj.get("metadata")
        if isinstance(obj.get("metadata"), dict)
        else (payload.get("metadata") if isinstance(payload.get("metadata"), dict) else {})
    )

    if prov == "creem":
        creem_res = await CreemAdapter().verify_webhook(
            payload=payload,
            headers=headers,
            merchant_config={},
            raw_body=raw_body,
        )
        event_type = str(payload.get("eventType") or payload.get("type") or "").lower()
        raw_biz = metadata.get("businessId") or metadata.get("business_id")
        biz_uuid: UUID | None = None
        if raw_biz:
            try:
                biz_uuid = UUID(str(raw_biz))
            except ValueError:
                biz_uuid = None

        ext_id = obj.get("request_id") or metadata.get("paymentId")
        payment = None
        if ext_id:
            try:
                payment = (await db.execute(select(Payment).where(Payment.id == UUID(str(ext_id))))).scalar_one_or_none()
            except ValueError:
                payment = None
        if not payment and creem_res.transaction_id:
            payment = (
                await db.execute(select(Payment).where(Payment.gateway_transaction_id == creem_res.transaction_id))
            ).scalar_one_or_none()

        if payment and not biz_uuid:
            biz_uuid = payment.business_id

        if creem_res.is_successful:
            if payment:
                payment.status = PaymentStatus.completed
                if payment.appointment_id:
                    from app.models.appointment import Appointment, AppointmentStatus
                    appt = (await db.execute(select(Appointment).where(Appointment.id == payment.appointment_id))).scalar_one_or_none()
                    if appt:
                        appt.status = AppointmentStatus.confirmed

            if biz_uuid and metadata.get("type") == "saas_subscription":
                biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
                if biz:
                    now = datetime.now(timezone.utc)
                    plan_uuid = biz.plan_id
                    if metadata.get("plan_id") or metadata.get("planId"):
                        try:
                            plan_uuid = UUID(str(metadata.get("plan_id") or metadata.get("planId")))
                            biz.plan_id = plan_uuid
                        except ValueError:
                            pass
                    biz.subscription_status = "active"
                    biz.is_active = True
                    biz.trial_ends_at = None
                    if plan_uuid:
                        sub = (await db.execute(select(Subscription).where(Subscription.business_id == biz.id))).scalars().first()
                        if sub:
                            sub.plan_id = plan_uuid
                            sub.status = SubscriptionStatus.active
                            sub.current_period_start = now
                            sub.current_period_end = now + timedelta(days=30)
                        else:
                            db.add(
                                Subscription(
                                    business_id=biz.id,
                                    plan_id=plan_uuid,
                                    status=SubscriptionStatus.active,
                                    current_period_start=now,
                                    current_period_end=now + timedelta(days=30),
                                )
                            )
            await db.commit()
            return {"status": "verified", "provider": "creem", "event": event_type}

        if biz_uuid and event_type in {"subscription.past_due", "subscription.unpaid", "subscription.canceled", "subscription.expired"}:
            biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
            if biz:
                biz.subscription_status = "past_due" if "past_due" in event_type or "unpaid" in event_type else "suspended"
            sub = (await db.execute(select(Subscription).where(Subscription.business_id == biz_uuid))).scalars().first()
            if sub:
                sub.status = SubscriptionStatus.past_due if "past_due" in event_type or "unpaid" in event_type else SubscriptionStatus.cancelled
            await db.commit()
            return {"status": "updated", "provider": "creem", "event": event_type}

        return {"status": "received", "provider": "creem", "event": event_type}

    # Try resolving business_id from metadata or existing Payment row (Payriff / Paymegate)
    biz_uuid = None
    raw_biz = metadata.get("businessId") or metadata.get("business_id") or payload.get("business_id")
    if raw_biz:
        try:
            biz_uuid = UUID(str(raw_biz))
        except ValueError:
            biz_uuid = None

    if not biz_uuid:
        ext_id = payload.get("externalId") or metadata.get("paymentId")
        order_uuid = payload.get("orderUUID") or payload.get("orderId")
        if ext_id:
            try:
                p_row = (
                    await db.execute(select(Payment).where(Payment.id == UUID(str(ext_id))))
                ).scalar_one_or_none()
                if p_row:
                    biz_uuid = p_row.business_id
            except ValueError:
                pass
        if not biz_uuid and order_uuid:
            p_row = (
                await db.execute(select(Payment).where(Payment.gateway_transaction_id == str(order_uuid)))
            ).scalar_one_or_none()
            if p_row:
                biz_uuid = p_row.business_id

    if biz_uuid:
        service = PaymentService(db=db, business_id=biz_uuid)
        verified = await service.handle_webhook_callback(provider=prov, payload=payload, headers=headers)
        if verified and metadata.get("type") == "saas_subscription" and metadata.get("plan_id"):
            from datetime import datetime, timedelta, timezone
            from app.models.business import Business
            from app.models.subscription import Subscription, SubscriptionStatus

            biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
            if biz:
                now = datetime.now(timezone.utc)
                try:
                    plan_uuid = UUID(str(metadata["plan_id"]))
                    biz.plan_id = plan_uuid
                except ValueError:
                    plan_uuid = biz.plan_id
                biz.subscription_status = "active"
                biz.is_active = True
                biz.trial_ends_at = None

                if plan_uuid:
                    sub = (
                        await db.execute(
                            select(Subscription).where(Subscription.business_id == biz.id)
                        )
                    ).scalars().first()
                    if sub:
                        sub.plan_id = plan_uuid
                        sub.status = SubscriptionStatus.active
                        sub.current_period_start = now
                        sub.current_period_end = now + timedelta(days=30)
                    else:
                        db.add(
                            Subscription(
                                business_id=biz.id,
                                plan_id=plan_uuid,
                                status=SubscriptionStatus.active,
                                current_period_start=now,
                                current_period_end=now + timedelta(days=30),
                            )
                        )
                await db.commit()
        return {"status": "verified" if verified else "ignored", "provider": prov}

    # Test / live event where payment row is not yet matched (e.g. Paymegate Dashboard "Test Webhook")
    if prov == "paymegate":
        result = await PaymegateAdapter().verify_webhook(payload=payload, headers=headers, merchant_config={})
        return {
            "status": "received",
            "provider": prov,
            "event": payload.get("type"),
            "verified": result.is_successful,
            "orderUUID": result.transaction_id,
        }

    return {"status": "received", "provider": prov}


@router.post("/payments/{provider}/{business_id}")
async def payment_gateway_webhook(
    provider: str,
    business_id: str,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """Handle incoming payment gateway webhooks from Payriff or PaymenGate."""
    try:
        biz_uuid = UUID(str(business_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid business ID")

    payload = await request.json()
    headers = dict(request.headers)
    service = PaymentService(db=db, business_id=biz_uuid)
    verified = await service.handle_webhook_callback(provider=provider, payload=payload, headers=headers)
    return {"status": "verified" if verified else "ignored", "provider": provider}
