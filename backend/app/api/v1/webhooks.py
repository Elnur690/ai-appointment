import logging
from datetime import datetime, timezone
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.integrations.whatsapp.webhook_handler import WebhookHandler
from app.services.guardrail_service import GuardrailService
from app.models.business import Business, Branch
from app.models.customer import Customer
from app.models.conversation import Conversation, Message, MessageDirection

logger = logging.getLogger(__name__)
router = APIRouter()
webhook_handler = WebhookHandler()
guardrail_service = GuardrailService()


@router.post("/whatsapp")
async def evolution_webhook(
    request: Request,
    apikey: str | None = Header(default=None),
    db: AsyncSession = Depends(get_db),
):
    """
    Receive Evolution API webhooks from internal container network:
    - Validates optional apikey header when provided
    - Parses message using WebhookHandler
    - Persists Customer, Conversation, and Message to PostgreSQL
    - Runs GuardrailService out-of-scope evaluation and updates conversation takeover state
    """
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

    # Persist incoming customer & message if a matching business exists in PostgreSQL
    try:
        biz = (await db.execute(select(Business).where(Business.is_active == True))).scalars().first()
        if biz and parsed.sender_phone and not parsed.is_group:
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

            if guardrail_result and guardrail_result.is_out_of_scope:
                conv.ai_active = False

            conv.last_message_at = datetime.now(timezone.utc)
            if parsed.message_text:
                db.add(
                    Message(
                        conversation_id=conv.id,
                        direction=MessageDirection.inbound,
                        sender_role="customer",
                        content=parsed.message_text,
                        message_type="text",
                        whatsapp_message_id=parsed.message_id,
                    )
                )
            await db.flush()
    except Exception as exc:
        logger.warning(f"Webhook persistence skipped: {exc}")

    return {
        "status": "ok",
        "instance": parsed.instance_name,
        "sender_phone": parsed.sender_phone,
        "is_group": parsed.is_group,
        "out_of_scope": guardrail_result.is_out_of_scope if guardrail_result else False,
    }
