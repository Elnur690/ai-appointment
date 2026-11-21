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
    """
    Receive Evolution API WhatsApp webhooks:
    1. Business Owner / Staff in WhatsApp Management Group:
       - Reply `#Q-XXX <answer>` to answer an escalated customer question, forward to customer, and save to RAG.
       - Ask management queries ("next customer?", "subscription status?", "today's schedule?", "revenue?").
    2. Customer 1-to-1 WhatsApp chat:
       - Run Gemini AI Receptionist with RAG Knowledge Base & booking tools and reply via Evolution API.
       - Escalate unanswered questions to the Business WhatsApp Group with a `#Q-XXX` ticket ID.
    """
    import json
    import re
    import secrets
    from app.models.business import BusinessOwner
    from app.models.staff import Staff
    from app.models.whatsapp import WhatsAppGroup, WhatsAppGroupScope, EscalationTicket
    from app.models.knowledge import KnowledgeEntry, KnowledgeEntryType, KnowledgeEntryStatus
    from app.integrations.whatsapp.client import EvolutionAPIClient
    from app.integrations.whatsapp.message_sender import WhatsAppMessageSender
    from app.integrations.ai.gemini import GeminiProvider
    from app.integrations.ai.provider import AIMessage, FinishReason
    from app.integrations.ai.tools import get_internal_group_tools
    from app.integrations.ai.internal_tool_executor import InternalGroupToolExecutor
    from app.integrations.ai.conversation_handler import ConversationHandler

    if apikey and settings.EVOLUTION_API_KEY and apikey != settings.EVOLUTION_API_KEY:
        if settings.ENVIRONMENT == "prod":
            raise HTTPException(status_code=401, detail="Invalid Evolution API webhook key")

    payload = await request.json()
    parsed = webhook_handler.parse_message(payload)
    if not parsed or parsed.is_from_me:
        return {"status": "ignored"}

    biz = None
    branch = None
    if parsed.instance_name:
        branch = (
            await db.execute(select(Branch).where(Branch.whatsapp_instance_id == parsed.instance_name))
        ).scalar_one_or_none()
        if branch:
            biz = (await db.execute(select(Business).where(Business.id == branch.business_id))).scalar_one_or_none()
    if not biz:
        biz = (await db.execute(select(Business).where(Business.is_active == True))).scalars().first()
        if biz and not branch:
            branch = (await db.execute(select(Branch).where(Branch.business_id == biz.id))).scalars().first()

    if not biz or not branch:
        return {"status": "ignored", "reason": "no_matching_business"}

    instance_name = parsed.instance_name or branch.whatsapp_instance_id or f"randevu_{str(biz.id)[:8]}_main"
    evo_client = EvolutionAPIClient(base_url=settings.EVOLUTION_API_URL, api_key=settings.EVOLUTION_API_KEY)
    wa_sender = WhatsAppMessageSender(evo_client)

    try:
        # ------------------------------------------------------------------
        # FLOW A: DEDICATED WHATSAPP MANAGEMENT GROUP (Owner / Staff)
        # ------------------------------------------------------------------
        if parsed.is_group and parsed.group_jid:
            group_row = (
                await db.execute(
                    select(WhatsAppGroup).where(
                        WhatsAppGroup.business_id == biz.id,
                        WhatsAppGroup.group_jid == parsed.group_jid,
                        WhatsAppGroup.is_active.is_(True),
                    )
                )
            ).scalar_one_or_none()

            # Strictly ignore all other groups not chosen as the dedicated group in Dashboard
            if not group_row:
                return {"status": "ignored", "reason": "not_dedicated_group"}

            # Determine sender role (owner vs staff)
            owner_match = (
                await db.execute(
                    select(BusinessOwner).where(
                        BusinessOwner.business_id == biz.id,
                        BusinessOwner.phone == parsed.sender_phone,
                    )
                )
            ).scalar_one_or_none()
            staff_match = (
                await db.execute(
                    select(Staff).where(
                        Staff.business_id == biz.id,
                        Staff.phone == parsed.sender_phone,
                    )
                )
            ).scalar_one_or_none()
            sender_role = "owner" if (owner_match or not staff_match) else "staff"

            msg_text = (parsed.message_text or "").strip()
            if not msg_text:
                return {"status": "ok", "channel": "whatsapp_group", "action": "empty"}

            # A1. Check if replying to an escalated question ticket: `#Q-1234 answer...`
            tag_match = re.search(r"#?(Q-\d{3,6})\b[:\-\s]*(.+)", msg_text, flags=re.IGNORECASE | re.DOTALL)
            if tag_match:
                ticket_code = tag_match.group(1).upper()
                answer_text = tag_match.group(2).strip()
                ticket = (
                    await db.execute(
                        select(EscalationTicket).where(
                            EscalationTicket.business_id == biz.id,
                            EscalationTicket.ticket_code == ticket_code,
                        )
                    )
                ).scalar_one_or_none()

                if ticket and answer_text:
                    ticket.status = "answered"
                    ticket.answer_text = answer_text
                    ticket.answered_at = datetime.now(timezone.utc)

                    # Re-enable AI and save Q&A into RAG KnowledgeEntry
                    if ticket.conversation_id:
                        conv = (
                            await db.execute(select(Conversation).where(Conversation.id == ticket.conversation_id))
                        ).scalar_one_or_none()
                        if conv:
                            conv.ai_active = True
                            db.add(
                                Message(
                                    conversation_id=conv.id,
                                    direction=MessageDirection.outbound,
                                    sender_role="owner",
                                    content=answer_text,
                                    message_type="text",
                                )
                            )

                    kb_entry = KnowledgeEntry(
                        business_id=biz.id,
                        branch_id=ticket.branch_id,
                        entry_type=KnowledgeEntryType.CORRECTION,
                        status=KnowledgeEntryStatus.ACTIVE,
                        title=ticket.question_text[:200],
                        question_context=ticket.question_text,
                        answer_content=answer_text,
                        conversation_id=ticket.conversation_id,
                    )
                    db.add(kb_entry)
                    await db.commit()

                    await wa_sender.send_response(
                        instance_name=instance_name,
                        to_phone=ticket.customer_phone,
                        text=answer_text,
                    )
                    await wa_sender.send_response(
                        instance_name=instance_name,
                        to_phone=parsed.group_jid,
                        text=f"✅ #{ticket_code} cavabı müştəriyə göndərildi və AI Bilik Bazasına (RAG) əlavə edildi.",
                    )
                    return {"status": "ok", "channel": "whatsapp_group", "ticket_resolved": ticket_code}

            # A2. General Business Owner / Staff management query in the group
            if settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("dev-"):
                ai = GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
                internal_exec = InternalGroupToolExecutor(
                    db=db,
                    business_id=biz.id,
                    branch_id=group_row.branch_id or branch.id,
                    sender_role=sender_role,
                    scope=group_row.scope.value if hasattr(group_row.scope, "value") else str(group_row.scope),
                )
                sys_prompt = (
                    f"You are the internal Randevu.vip executive assistant for '{biz.name}'. "
                    "Answer the business owner/staff concisely in the same language they wrote (Azerbaijani by default). "
                    "Use the provided tools to check next customer, schedule, revenue, no-shows, or subscription status."
                )
                msgs = [AIMessage(role="user", content=msg_text)]
                tools = get_internal_group_tools()
                for _ in range(4):
                    ai_res = await ai.generate_response(messages=msgs, system_prompt=sys_prompt, tools=tools)
                    msgs.append(AIMessage(role="assistant", content=ai_res.text, tool_calls=ai_res.tool_calls))
                    if ai_res.finish_reason == FinishReason.TOOL_CALL and ai_res.tool_calls:
                        for tc in ai_res.tool_calls:
                            t_res = await internal_exec.execute(tc)
                            msgs.append(
                                AIMessage(
                                    role="tool",
                                    content=json.dumps(t_res),
                                    tool_call_id=tc.id,
                                    tool_name=tc.name,
                                )
                            )
                    else:
                        break
                reply_text = msgs[-1].content if msgs and msgs[-1].content else None
                if reply_text:
                    await wa_sender.send_response(
                        instance_name=instance_name,
                        to_phone=parsed.group_jid,
                        text=reply_text,
                    )
            await db.commit()
            return {"status": "ok", "channel": "whatsapp_group", "group_jid": parsed.group_jid}

        # ------------------------------------------------------------------
        # FLOW B: CUSTOMER 1-TO-1 WHATSAPP AI RECEPTIONIST
        # ------------------------------------------------------------------
        # Check business-configured excluded phone numbers (numbers that must NOT receive AI bot replies)
        tone_cfg = biz.default_ai_tone_config or {}
        raw_excluded = tone_cfg.get("excluded_phone_numbers") or ""
        if isinstance(raw_excluded, str):
            excluded_list = [re.sub(r"\D", "", item) for item in re.split(r"[,\n;]+", raw_excluded) if item.strip()]
        elif isinstance(raw_excluded, list):
            excluded_list = [re.sub(r"\D", "", str(item)) for item in raw_excluded if str(item).strip()]
        else:
            excluded_list = []

        sender_digits = re.sub(r"\D", "", parsed.sender_phone or "")
        if sender_digits and any(
            ex and (sender_digits == ex or sender_digits.endswith(ex) or ex.endswith(sender_digits))
            for ex in excluded_list
        ):
            return {
                "status": "ignored",
                "channel": "whatsapp",
                "reason": "excluded_number",
                "sender_phone": parsed.sender_phone,
            }

        guardrail_result = None
        if parsed.message_text:
            guardrail_result = guardrail_service.evaluate_message(
                message_text=parsed.message_text,
                language="az",
                is_solo_business=False,
            )

        conv = await _persist_incoming_message(
            db=db,
            biz=biz,
            parsed=parsed,
            guardrail_out_of_scope=bool(guardrail_result and guardrail_result.is_out_of_scope),
        )

        escalate = bool(guardrail_result and guardrail_result.is_out_of_scope)
        ai_reply: str | None = None

        if not escalate and parsed.message_text and settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("dev-"):
            ai = GeminiProvider(api_key=settings.GEMINI_API_KEY, model_name=settings.GEMINI_MODEL)
            handler = ConversationHandler(
                db=db,
                ai_provider=ai,
                business_id=biz.id,
                branch_id=branch.id,
            )
            conv_res = await handler.handle_incoming_message(
                customer_phone=parsed.sender_phone,
                message_text=parsed.message_text,
                customer_name=parsed.sender_name,
            )
            ai_reply = conv_res.response_text
            if conv_res.human_handoff_requested:
                escalate = True

        if ai_reply:
            await wa_sender.send_response(
                instance_name=instance_name,
                to_phone=parsed.sender_phone,
                text=ai_reply,
            )

        if escalate and parsed.message_text:
            ticket_code = f"Q-{100 + secrets.randbelow(900)}"
            ticket = EscalationTicket(
                ticket_code=ticket_code,
                business_id=biz.id,
                branch_id=branch.id,
                conversation_id=conv.id if conv else None,
                customer_id=conv.customer_id if conv else None,
                customer_phone=parsed.sender_phone,
                question_text=parsed.message_text,
                status="open",
            )
            db.add(ticket)
            await db.flush()

            grp = (
                await db.execute(
                    select(WhatsAppGroup).where(WhatsAppGroup.business_id == biz.id, WhatsAppGroup.is_active.is_(True))
                )
            ).scalars().first()
            target_jid = grp.group_jid if grp else None
            if not target_jid:
                owner = (
                    await db.execute(select(BusinessOwner).where(BusinessOwner.business_id == biz.id))
                ).scalars().first()
                target_jid = owner.phone if owner and owner.phone else None

            if target_jid:
                esc_msg = (
                    f"❓ [#{ticket_code}] Müştəri sualı ({parsed.sender_phone}):\n"
                    f"\"{parsed.message_text}\"\n\n"
                    f"Cavab vermək üçün yazın:\n"
                    f"#{ticket_code} Sizin cavabınız"
                )
                await wa_sender.send_response(
                    instance_name=instance_name,
                    to_phone=target_jid,
                    text=esc_msg,
                )

        await db.commit()
        return {
            "status": "ok",
            "channel": "whatsapp",
            "instance": instance_name,
            "sender_phone": parsed.sender_phone,
            "is_group": parsed.is_group,
            "escalated": escalate,
        }
    finally:
        await evo_client.close()


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
                        creem_sub_id = (
                            (obj.get("subscription") or {}).get("id")
                            if isinstance(obj.get("subscription"), dict)
                            else (obj.get("id") if event_type.startswith("subscription.") else obj.get("subscription"))
                        )
                        creem_cust_id = (
                            (obj.get("customer") or {}).get("id")
                            if isinstance(obj.get("customer"), dict)
                            else obj.get("customer_id")
                        )
                        sub = (await db.execute(select(Subscription).where(Subscription.business_id == biz.id))).scalars().first()
                        if sub:
                            sub.plan_id = plan_uuid
                            sub.status = SubscriptionStatus.active
                            sub.current_period_start = now
                            sub.current_period_end = now + timedelta(days=30)
                            if creem_sub_id:
                                sub.creem_subscription_id = str(creem_sub_id)
                            if creem_cust_id:
                                sub.creem_customer_id = str(creem_cust_id)
                        else:
                            db.add(
                                Subscription(
                                    business_id=biz.id,
                                    plan_id=plan_uuid,
                                    status=SubscriptionStatus.active,
                                    current_period_start=now,
                                    current_period_end=now + timedelta(days=30),
                                    creem_subscription_id=str(creem_sub_id) if creem_sub_id else None,
                                    creem_customer_id=str(creem_cust_id) if creem_cust_id else None,
                                )
                            )
            await db.commit()
            return {"status": "verified", "provider": "creem", "event": event_type}

        if biz_uuid and event_type == "subscription.trialing":
            biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
            if biz:
                biz.subscription_status = "trial"
                biz.is_active = True
            sub = (await db.execute(select(Subscription).where(Subscription.business_id == biz_uuid))).scalars().first()
            if sub:
                sub.status = SubscriptionStatus.trial
            await db.commit()
            return {"status": "updated", "provider": "creem", "event": event_type}

        if event_type in {"refund.created", "dispute.created"}:
            if payment:
                payment.status = PaymentStatus.refunded
                await db.commit()
            return {"status": "refunded", "provider": "creem", "event": event_type}

        if biz_uuid and event_type in {
            "subscription.past_due",
            "subscription.unpaid",
            "subscription.canceled",
            "subscription.expired",
            "subscription.paused",
        }:
            biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
            is_past_due = event_type in {"subscription.past_due", "subscription.unpaid"}
            is_expired = event_type == "subscription.expired"
            if biz:
                biz.subscription_status = "past_due" if is_past_due else "suspended"
            sub = (await db.execute(select(Subscription).where(Subscription.business_id == biz_uuid))).scalars().first()
            if sub:
                sub.status = (
                    SubscriptionStatus.past_due
                    if is_past_due
                    else (SubscriptionStatus.expired if is_expired else SubscriptionStatus.cancelled)
                )
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

    content_type = (request.headers.get("content-type") or "").lower()
    if "application/x-www-form-urlencoded" in content_type or "multipart/form-data" in content_type:
        form_data = await request.form()
        payload = {k: v for k, v in form_data.items()}
    else:
        try:
            payload = await request.json()
        except Exception:
            raw_txt = (await request.body()).decode("utf-8", errors="ignore")
            from urllib.parse import parse_qs
            parsed_qs = parse_qs(raw_txt)
            payload = {k: v[0] for k, v in parsed_qs.items()} if parsed_qs else {}
    headers = dict(request.headers)
    service = PaymentService(db=db, business_id=biz_uuid)
    verified = await service.handle_webhook_callback(provider=provider, payload=payload, headers=headers)
    return {"status": "verified" if verified else "ignored", "provider": provider}
