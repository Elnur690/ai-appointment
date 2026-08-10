from typing import Annotated, Any, List
from datetime import datetime, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class AppointmentBase(BaseModel):
    customer_id: str
    service_id: str
    staff_id: str
    start_time: datetime
    end_time: datetime

class AppointmentCreate(AppointmentBase):
    branch_id: str | None = None

class AppointmentUpdate(BaseModel):
    status: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None

class AppointmentResponse(AppointmentBase):
    id: str
    business_id: str
    branch_id: str
    status: str

class AvailableSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    staff_id: str

@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    branch_id: str | None = None,
    staff_id: str | None = None,
    status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List appointments with filters."""
    return []

@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Create appointment manually."""
    return AppointmentResponse(
        id="temp", business_id=business_id, branch_id=appointment.branch_id or "default",
        status="scheduled", **appointment.model_dump()
    )

@router.get("/calendar", response_model=List[AppointmentResponse])
async def get_appointments_calendar(
    start_date: date,
    end_date: date,
    branch_id: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get appointments for calendar view."""
    return []

@router.get("/availability", response_model=List[AvailableSlot])
async def check_availability(
    service_id: str,
    target_date: date,
    staff_id: str | None = None,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Check available slots."""
    return []

@router.get("/{id}", response_model=AppointmentResponse)
async def get_appointment(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get appointment by ID."""
    return AppointmentResponse(
        id=id, business_id=business_id, branch_id="default",
        customer_id="cust", service_id="serv", staff_id="staff",
        start_time=datetime.now(), end_time=datetime.now(), status="scheduled"
    )

@router.put("/{id}", response_model=AppointmentResponse)
async def update_appointment(
    id: str,
    update_data: AppointmentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Update appointment status or reschedule."""
    return AppointmentResponse(
        id=id, business_id=business_id, branch_id="default",
        customer_id="cust", service_id="serv", staff_id="staff",
        start_time=update_data.start_time or datetime.now(),
        end_time=update_data.end_time or datetime.now(),
        status=update_data.status or "scheduled"
    )
