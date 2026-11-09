import logging
from fastapi import APIRouter, Request, Header, HTTPException
from app.core.config import settings
from app.integrations.whatsapp.webhook_handler import WebhookHandler
from app.services.guardrail_service import GuardrailService

logger = logging.getLogger(__name__)
router = APIRouter()
webhook_handler = WebhookHandler()
guardrail_service = GuardrailService()


@router.post("/whatsapp")
async def evolution_webhook(
    request: Request,
    apikey: str | None = Header(default=None),
):
    """
    Receive Evolution API webhooks from internal container network.
    - Validates optional apikey header when provided
    - Parses message using WebhookHandler
    - Runs GuardrailService out-of-scope & solo-business human-tone evaluation
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

    return {
        "status": "ok",
        "instance": parsed.instance_name,
        "sender_phone": parsed.sender_phone,
        "is_group": parsed.is_group,
        "out_of_scope": guardrail_result.is_out_of_scope if guardrail_result else False,
    }
