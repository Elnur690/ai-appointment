from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class CustomerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    phone_number: str
    name: Optional[str]
    language_pref: str = "az"
    created_at: datetime

class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    language_pref: Optional[str] = None
