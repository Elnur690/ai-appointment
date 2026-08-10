from typing import Optional, List
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.schemas.customer import CustomerResponse

class ConversationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    customer_id: UUID
    context_type: str
    ai_active: bool
    last_message_at: datetime

class MessageResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    direction: str
    sender_role: str
    content: str
    message_type: str
    intent_detected: Optional[str]
    created_at: datetime

class ConversationDetailResponse(BaseModel):
    conversation: ConversationResponse
    messages: List[MessageResponse]
    customer: Optional[CustomerResponse] = None
