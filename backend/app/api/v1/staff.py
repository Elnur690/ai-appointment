from typing import Annotated, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class StaffBase(BaseModel):
    name: str
    email: str | None = None
    phone: str | None = None
    branch_id: str | None = None

class StaffCreate(StaffBase):
    pass

class StaffUpdate(BaseModel):
    name: str | None = None
    email: str | None = None
    phone: str | None = None
    branch_id: str | None = None

class StaffResponse(StaffBase):
    id: str
    business_id: str
    is_active: bool

class StaffScheduleCreate(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str

class StaffScheduleResponse(StaffScheduleCreate):
    id: str

@router.get("/", response_model=List[StaffResponse])
async def list_staff(
    branch_id: str | None = Query(None),
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List staff members, optionally filtered by branch."""
    return []

@router.post("/", response_model=StaffResponse)
async def create_staff(
    staff: StaffCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Create a new staff member."""
    return StaffResponse(id="temp", business_id=business_id, **staff.model_dump(), is_active=True)

@router.get("/{id}", response_model=StaffResponse)
async def get_staff(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get staff member details."""
    return StaffResponse(id=id, business_id=business_id, name="Placeholder", is_active=True)

@router.put("/{id}", response_model=StaffResponse)
async def update_staff(
    id: str,
    staff_update: StaffUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Update a staff member."""
    return StaffResponse(id=id, business_id=business_id, name="Updated", is_active=True)

@router.delete("/{id}")
async def deactivate_staff(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Deactivate a staff member."""
    return {"status": "success"}

@router.get("/{id}/schedules", response_model=List[StaffScheduleResponse])
async def get_staff_schedules(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get staff schedules."""
    return []

@router.put("/{id}/schedules", response_model=List[StaffScheduleResponse])
async def update_staff_schedules(
    id: str,
    schedules: List[StaffScheduleCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Bulk update staff schedules."""
    return []

@router.get("/{id}/services", response_model=List[str])
async def get_staff_services(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get assigned services for a staff member."""
    return []

@router.put("/{id}/services")
async def assign_staff_services(
    id: str,
    service_ids: List[str],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Assign services to staff member."""
    return {"status": "success", "service_ids": service_ids}
