from typing import Optional
from uuid import UUID
from datetime import time
from pydantic import BaseModel, EmailStr, ConfigDict

class StaffCreate(BaseModel):
    name: str
    role: str
    branch_id: UUID
    phone: Optional[str] = None
    email: Optional[EmailStr] = None

class StaffUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None

class StaffResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    role: str
    phone: Optional[str]
    email: Optional[EmailStr]
    branch_id: UUID
    is_active: bool

class StaffScheduleCreate(BaseModel):
    day_of_week: int
    start_time: time
    end_time: time

class StaffScheduleUpdate(BaseModel):
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class StaffScheduleResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    day_of_week: int
    start_time: time
    end_time: time
    staff_id: UUID

class StaffServiceAssign(BaseModel):
    service_ids: list[UUID]
