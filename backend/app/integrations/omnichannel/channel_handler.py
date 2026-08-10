import logging
from app.integrations.whatsapp.webhook_handler import ParsedWebhookMessage

logger = logging.getLogger(__name__)

class OmnichannelHandler:
    """Normalizes Instagram Direct Messages & Facebook Messenger webhooks into standard ParsedWebhookMessage."""

    def parse_meta_webhook(self, payload: dict, channel: str = "instagram") -> ParsedWebhookMessage | None:
        """Parse Meta Webhook payload (Instagram DM or Facebook Messenger)."""
        try:
            entries = payload.get("entry", [])
            if not entries:
                return None

            entry = entries[0]
            messaging = entry.get("messaging", [])
            if not messaging:
                return None

            event = messaging[0]
            sender_id = event.get("sender", {}).get("id", "unknown_sender")
            recipient_id = event.get("recipient", {}).get("id", "unknown_recipient")
            message = event.get("message", {})
            
            message_id = message.get("mid", "meta_msg_id")
            message_text = message.get("text")
            
            logger.info(f"[OMNICHANNEL {channel.upper()}] Parsed DM from sender '{sender_id}': {message_text}")
            
            return ParsedWebhookMessage(
                instance_name=f"{channel}_instance_{recipient_id}",
                sender_jid=f"{sender_id}@{channel}.com",
                sender_phone=sender_id,
                sender_name=f"{channel.capitalize()} User",
                message_text=message_text,
                message_type="text",
                message_id=message_id,
                is_group=False,
                group_jid=None,
                timestamp=event.get("timestamp", 0),
                is_from_me=False,
            )
        except Exception as e:
            logger.error(f"Failed to parse Omnichannel {channel} payload: {e}")
            return None
