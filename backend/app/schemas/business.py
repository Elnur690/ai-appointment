from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict

class BusinessCreate(BaseModel):
    name: str
    default_ai_tone_config: Optional[Dict[str, Any]] = None

class BusinessUpdate(BaseModel):
    name: Optional[str] = None
    default_ai_tone_config: Optional[Dict[str, Any]] = None

class BusinessResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    subscription_status: str
    default_ai_tone_config: Optional[Dict[str, Any]]
    is_active: bool
    plan_id: Optional[UUID]
    created_at: datetime

class BusinessOwnerCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: Optional[str] = None

class BusinessOwnerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    email: EmailStr
    phone: Optional[str]
    is_active: bool
