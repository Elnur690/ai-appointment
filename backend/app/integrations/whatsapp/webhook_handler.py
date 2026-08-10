from dataclasses import dataclass

@dataclass
class ParsedWebhookMessage:
    instance_name: str
    sender_jid: str
    sender_phone: str
    sender_name: str | None
    message_text: str | None
    message_type: str
    message_id: str
    is_group: bool
    group_jid: str | None
    timestamp: int
    is_from_me: bool

class WebhookHandler:
    def parse_message(self, payload: dict) -> ParsedWebhookMessage | None:
        """Parse Evolution API MESSAGES_UPSERT webhook payload."""
        
        # Check if it's the right event type
        if payload.get("event") != "messages.upsert":
            return None
            
        data = payload.get("data", {})
        message_data = data.get("message", {})
        key = data.get("key", {})
        
        if not key or not message_data:
            return None
            
        is_from_me = key.get("fromMe", False)
        
        # We usually ignore messages we sent, unless debugging
        # if is_from_me:
        #    return None
            
        remote_jid = key.get("remoteJid", "")
        message_id = key.get("id", "")
        
        is_group = "@g.us" in remote_jid
        sender_jid = data.get("pushName") if is_group else remote_jid # In groups, the sender is in participant or we can get it from the actual jid if provided
        group_jid = remote_jid if is_group else None
        
        if is_group:
            sender_jid = data.get("participant", remote_jid)

        sender_phone = sender_jid.split("@")[0]
        sender_name = data.get("pushName")
        timestamp = data.get("messageTimestamp", 0)
        
        message_type = "unknown"
        message_text = None
        
        if "conversation" in message_data:
            message_type = "text"
            message_text = message_data["conversation"]
        elif "extendedTextMessage" in message_data:
            message_type = "text"
            message_text = message_data["extendedTextMessage"].get("text")
        elif "imageMessage" in message_data:
            message_type = "image"
            message_text = message_data["imageMessage"].get("caption")
        elif "audioMessage" in message_data:
            message_type = "audio"
            audio = message_data["audioMessage"]
            message_text = audio.get("url") or audio.get("directPath") or "[Voice Note]"
        elif "pttMessage" in message_data:
            message_type = "audio"
            audio = message_data["pttMessage"]
            message_text = audio.get("url") or audio.get("directPath") or "[Voice Note]"
            
        instance_name = payload.get("instance", "")
        
        return ParsedWebhookMessage(
            instance_name=instance_name,
            sender_jid=sender_jid,
            sender_phone=sender_phone,
            sender_name=sender_name,
            message_text=message_text,
            message_type=message_type,
            message_id=message_id,
            is_group=is_group,
            group_jid=group_jid,
            timestamp=timestamp,
            is_from_me=is_from_me
        )
