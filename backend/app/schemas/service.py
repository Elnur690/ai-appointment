from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict

class ServiceCreate(BaseModel):
    name: str
    description: Optional[str] = None
    duration_minutes: int
    price: float
    buffer_minutes: Optional[int] = 0
    branch_id: Optional[UUID] = None

class ServiceUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    duration_minutes: Optional[int] = None
    price: Optional[float] = None
    buffer_minutes: Optional[int] = None
    is_active: Optional[bool] = None

class ServiceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    description: Optional[str]
    duration_minutes: int
    price: float
    buffer_minutes: int
    is_active: bool
    branch_id: Optional[UUID]
