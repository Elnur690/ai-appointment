from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PaymentCreate(BaseModel):
    appointment_id: Optional[UUID] = None
    amount: float
    method: str
    notes: Optional[str] = None

class PaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    appointment_id: Optional[UUID]
    amount: float
    currency: str
    method: str
    status: str
    recorded_by: Optional[UUID]
    notes: Optional[str]
    created_at: datetime
