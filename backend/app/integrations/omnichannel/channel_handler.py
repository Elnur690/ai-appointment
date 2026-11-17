import logging
import httpx
from app.integrations.whatsapp.webhook_handler import ParsedWebhookMessage

logger = logging.getLogger(__name__)


class OmnichannelHandler:
    """Normalizes Instagram Direct Messages, Facebook Messenger, and Telegram Bot webhooks into standard ParsedWebhookMessage."""

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
            if event.get("message", {}).get("is_echo"):
                return None

            sender_id = str(event.get("sender", {}).get("id", "unknown_sender"))
            recipient_id = str(event.get("recipient", {}).get("id", "unknown_recipient"))
            message = event.get("message", {})

            message_id = str(message.get("mid", "meta_msg_id"))
            message_text = message.get("text")

            logger.info(f"[OMNICHANNEL {channel.upper()}] Parsed DM from sender '{sender_id}': {message_text}")

            return ParsedWebhookMessage(
                instance_name=f"{channel}_instance_{recipient_id}",
                sender_jid=f"{sender_id}@{channel}.com",
                sender_phone=f"ig:{sender_id}",
                sender_name=f"{channel.capitalize()} ({sender_id[-4:]})",
                message_text=message_text,
                message_type="text",
                message_id=message_id,
                is_group=False,
                group_jid=None,
                timestamp=int(event.get("timestamp", 0)),
                is_from_me=False,
            )
        except Exception as e:
            logger.error(f"Failed to parse Omnichannel {channel} payload: {e}")
            return None

    def parse_telegram_webhook(self, payload: dict, business_id: str = "default") -> ParsedWebhookMessage | None:
        """Parse Telegram Bot API Update payload into standard ParsedWebhookMessage."""
        try:
            msg = payload.get("message") or payload.get("edited_message")
            if not msg:
                return None

            chat = msg.get("chat", {})
            sender = msg.get("from", {})
            if sender.get("is_bot"):
                return None

            chat_id = str(chat.get("id", ""))
            chat_type = chat.get("type", "private")
            is_group = chat_type in {"group", "supergroup"}

            first_name = sender.get("first_name", "")
            last_name = sender.get("last_name", "")
            username = sender.get("username", "")
            full_name = f"{first_name} {last_name}".strip() or (f"@{username}" if username else f"TG {chat_id}")

            text = msg.get("text") or msg.get("caption") or ""
            msg_id = f"tg_{chat_id}_{msg.get('message_id', '')}"

            return ParsedWebhookMessage(
                instance_name=f"telegram_{business_id}",
                sender_jid=f"{chat_id}@telegram.org",
                sender_phone=f"tg:{chat_id}",
                sender_name=full_name,
                message_text=text,
                message_type="text",
                message_id=msg_id,
                is_group=is_group,
                group_jid=f"{chat_id}@telegram.group" if is_group else None,
                timestamp=int(msg.get("date", 0)),
                is_from_me=False,
            )
        except Exception as exc:
            logger.error(f"Failed to parse Telegram webhook payload: {exc}")
            return None

    async def send_telegram_message(self, bot_token: str, chat_id: str, text: str) -> bool:
        """Send an outbound message through Telegram Bot API."""
        clean_chat_id = str(chat_id).replace("tg:", "").replace("@telegram.org", "")
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(url, json={"chat_id": clean_chat_id, "text": text})
                return resp.status_code == 200
        except Exception as exc:
            logger.warning(f"Telegram sendMessage failed: {exc}")
            return False

    async def send_instagram_message(self, page_access_token: str, recipient_id: str, text: str) -> bool:
        """Send an outbound Instagram Direct message via Meta Graph API."""
        clean_recipient = str(recipient_id).replace("ig:", "").replace("@instagram.com", "")
        url = "https://graph.facebook.com/v21.0/me/messages"
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    url,
                    params={"access_token": page_access_token},
                    json={
                        "recipient": {"id": clean_recipient},
                        "message": {"text": text},
                    },
                )
                return resp.status_code in (200, 201)
        except Exception as exc:
            logger.warning(f"Instagram Graph API send failed: {exc}")
            return False
