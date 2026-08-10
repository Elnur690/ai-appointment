from typing import Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class BranchCreate(BaseModel):
    name: str
    location: Optional[str] = None
    working_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = "UTC"

class BranchUpdate(BaseModel):
    name: Optional[str] = None
    location: Optional[str] = None
    working_hours: Optional[Dict[str, Any]] = None
    timezone: Optional[str] = None
    ai_tone_config: Optional[Dict[str, Any]] = None

class BranchResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    location: Optional[str]
    working_hours: Optional[Dict[str, Any]]
    timezone: str
    whatsapp_instance_id: Optional[str]
    ai_tone_config: Optional[Dict[str, Any]]
    is_active: bool
