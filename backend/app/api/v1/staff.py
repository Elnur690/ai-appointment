from datetime import time
from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.business import Branch
from app.models.staff import Staff, StaffSchedule, StaffService

router = APIRouter()


class StaffBase(BaseModel):
    name: str
    role: str | None = "Specialist"
    phone: str | None = None
    email: str | None = None
    branch_id: str | None = None
    shift_type: str | None = "full_day"
    allow_overtime: bool = False
    max_overtime_minutes: int = 60


class StaffCreate(StaffBase):
    pass


class StaffUpdate(BaseModel):
    name: str | None = None
    role: str | None = None
    phone: str | None = None
    email: str | None = None
    branch_id: str | None = None
    shift_type: str | None = None
    allow_overtime: bool | None = None
    max_overtime_minutes: int | None = None
    is_active: bool | None = None


class StaffResponse(StaffBase):
    id: str
    business_id: str
    is_active: bool


class StaffScheduleCreate(BaseModel):
    day_of_week: int
    start_time: str
    end_time: str
    shift_type: str = "full_day"
    allow_overtime: bool = False
    max_overtime_minutes: int = 60


class StaffScheduleResponse(StaffScheduleCreate):
    id: str


async def _resolve_branch_id(db: AsyncSession, business_id: UUID, branch_id: str | None) -> UUID:
    if branch_id:
        try:
            return UUID(branch_id)
        except ValueError:
            pass
    stmt = select(Branch).where(Branch.business_id == business_id).order_by(Branch.created_at.asc())
    branch = (await db.execute(stmt)).scalars().first()
    if branch:
        return branch.id
    new_branch = Branch(business_id=business_id, name="Main Branch", timezone="Asia/Baku", is_active=True)
    db.add(new_branch)
    await db.flush()
    return new_branch.id


def _to_response(s: Staff) -> StaffResponse:
    return StaffResponse(
        id=str(s.id),
        business_id=str(s.business_id),
        branch_id=str(s.branch_id),
        name=s.name,
        role=s.role,
        phone=s.phone,
        email=s.email,
        is_active=bool(s.is_active),
    )


@router.get("/", response_model=List[StaffResponse])
async def list_staff(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    branch_id: str | None = Query(None),
):
    """List staff members from PostgreSQL, optionally filtered by branch."""
    stmt = select(Staff).where(Staff.business_id == UUID(business_id))
    if branch_id:
        try:
            stmt = stmt.where(Staff.branch_id == UUID(branch_id))
        except ValueError:
            pass
    stmt = stmt.order_by(Staff.created_at.asc())
    res = await db.execute(stmt)
    return [_to_response(s) for s in res.scalars().all()]


@router.post("/", response_model=StaffResponse)
async def create_staff(
    staff: StaffCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create a new staff member in PostgreSQL."""
    biz_uuid = UUID(business_id)
    branch_uuid = await _resolve_branch_id(db, biz_uuid, staff.branch_id)
    new_staff = Staff(
        business_id=biz_uuid,
        branch_id=branch_uuid,
        name=staff.name.strip(),
        role=staff.role or "Specialist",
        phone=staff.phone,
        email=staff.email,
        is_active=True,
    )
    db.add(new_staff)
    await db.flush()
    return _to_response(new_staff)


@router.get("/{id}", response_model=StaffResponse)
async def get_staff(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get staff member details."""
    stmt = select(Staff).where(Staff.id == UUID(id), Staff.business_id == UUID(business_id))
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Staff member not found")
    return _to_response(s)


@router.put("/{id}", response_model=StaffResponse)
@router.patch("/{id}", response_model=StaffResponse)
async def update_staff(
    id: str,
    staff_update: StaffUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update a staff member."""
    stmt = select(Staff).where(Staff.id == UUID(id), Staff.business_id == UUID(business_id))
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Staff member not found")
    for k, v in staff_update.model_dump(exclude_unset=True).items():
        if hasattr(s, k) and k != "branch_id":
            setattr(s, k, v)
    await db.flush()
    return _to_response(s)


@router.delete("/{id}")
async def deactivate_staff(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Deactivate a staff member."""
    stmt = select(Staff).where(Staff.id == UUID(id), Staff.business_id == UUID(business_id))
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Staff member not found")
    s.is_active = False
    await db.flush()
    return {"status": "success"}


@router.get("/{id}/schedules", response_model=List[StaffScheduleResponse])
async def get_staff_schedules(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get staff schedules."""
    stmt = select(StaffSchedule).where(StaffSchedule.staff_id == UUID(id))
    res = await db.execute(stmt)
    return [
        StaffScheduleResponse(
            id=str(sc.id),
            day_of_week=sc.day_of_week,
            start_time=sc.start_time.strftime("%H:%M"),
            end_time=sc.end_time.strftime("%H:%M"),
            shift_type=sc.shift_type,
            allow_overtime=bool(sc.allow_overtime),
            max_overtime_minutes=sc.max_overtime_minutes,
        )
        for sc in res.scalars().all()
    ]


@router.put("/{id}/schedules", response_model=List[StaffScheduleResponse])
async def update_staff_schedules(
    id: str,
    schedules: List[StaffScheduleCreate],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Bulk update staff schedules."""
    staff_uuid = UUID(id)
    await db.execute(delete(StaffSchedule).where(StaffSchedule.staff_id == staff_uuid))
    created = []
    for sc in schedules:
        sh, sm = [int(x) for x in sc.start_time.split(":")[:2]]
        eh, em = [int(x) for x in sc.end_time.split(":")[:2]]
        row = StaffSchedule(
            staff_id=staff_uuid,
            day_of_week=sc.day_of_week,
            start_time=time(sh, sm),
            end_time=time(eh, em),
            shift_type=sc.shift_type,
            allow_overtime=sc.allow_overtime,
            max_overtime_minutes=sc.max_overtime_minutes,
        )
        db.add(row)
        created.append(row)
    await db.flush()
    return [
        StaffScheduleResponse(
            id=str(r.id),
            day_of_week=r.day_of_week,
            start_time=r.start_time.strftime("%H:%M"),
            end_time=r.end_time.strftime("%H:%M"),
            shift_type=r.shift_type,
            allow_overtime=bool(r.allow_overtime),
            max_overtime_minutes=r.max_overtime_minutes,
        )
        for r in created
    ]


@router.get("/{id}/services", response_model=List[str])
async def get_staff_services(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get assigned services for a staff member."""
    stmt = select(StaffService).where(StaffService.staff_id == UUID(id))
    res = await db.execute(stmt)
    return [str(ss.service_id) for ss in res.scalars().all()]


@router.put("/{id}/services")
async def assign_staff_services(
    id: str,
    service_ids: List[str],
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Assign services to staff member."""
    staff_uuid = UUID(id)
    await db.execute(delete(StaffService).where(StaffService.staff_id == staff_uuid))
    for sid in service_ids:
        db.add(StaffService(staff_id=staff_uuid, service_id=UUID(sid)))
    await db.flush()
    return {"status": "success", "service_ids": service_ids}
