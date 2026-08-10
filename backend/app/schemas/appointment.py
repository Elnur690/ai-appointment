from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.models.appointment import AppointmentStatus

class AppointmentCreate(BaseModel):
    service_id: UUID
    staff_id: UUID
    start_time: datetime
    customer_id: Optional[UUID] = None
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

class AppointmentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    branch_id: UUID
    staff_id: UUID
    customer_id: UUID
    service_id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    source: str
    notes: Optional[str]
    created_at: datetime
    
    staff_name: Optional[str] = None
    service_name: Optional[str] = None
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None

class AppointmentCalendarResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    start_time: datetime
    end_time: datetime
    status: AppointmentStatus
    service_name: str
    staff_name: str
    customer_name: Optional[str]

class AvailableSlotResponse(BaseModel):
    staff_id: UUID
    staff_name: str
    start_time: datetime
    end_time: datetime
    date: str
    time: str
