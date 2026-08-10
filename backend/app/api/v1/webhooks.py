from typing import Annotated, Any, Dict
from fastapi import APIRouter, Request, BackgroundTasks

router = APIRouter()

@router.post("/whatsapp")
async def evolution_webhook(
    request: Request,
    background_tasks: BackgroundTasks
):
    """
    Receive Evolution API webhooks.
    - Validate the webhook (check event type, extract data)
    - Parse using WebhookHandler
    - Enqueue Celery task for async processing
    - Return 200 immediately
    """
    payload = await request.json()
    
    # TODO: Validate webhook structure, verify signature if applicable
    # event_type = payload.get("event")
    
    # TODO: Enqueue Celery task for processing instead of BackgroundTasks
    # process_whatsapp_message.delay(payload)
    
    return {"status": "ok"}
