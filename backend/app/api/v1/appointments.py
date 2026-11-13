from datetime import date, datetime, time, timezone
from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.appointment import Appointment, AppointmentStatus, AppointmentSource
from app.models.business import Branch
from app.models.customer import Customer
from app.models.service import Service
from app.models.staff import Staff

router = APIRouter()


class AppointmentBase(BaseModel):
    customer_id: str | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    service_id: str | None = None
    staff_id: str | None = None
    start_time: datetime
    end_time: datetime | None = None
    notes: str | None = None


class AppointmentCreate(AppointmentBase):
    branch_id: str | None = None


class AppointmentUpdate(BaseModel):
    status: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    staff_id: str | None = None
    notes: str | None = None


class AppointmentResponse(BaseModel):
    id: str
    business_id: str
    branch_id: str
    customer_id: str
    customer_name: str | None = None
    customer_phone: str | None = None
    service_id: str
    service_name: str | None = None
    staff_id: str
    staff_name: str | None = None
    start_time: datetime
    end_time: datetime
    status: str
    notes: str | None = None


class AvailableSlot(BaseModel):
    start_time: datetime
    end_time: datetime
    staff_id: str


def _to_response(a: Appointment) -> AppointmentResponse:
    return AppointmentResponse(
        id=str(a.id),
        business_id=str(a.business_id),
        branch_id=str(a.branch_id),
        customer_id=str(a.customer_id),
        customer_name=a.customer.name if a.customer else None,
        customer_phone=a.customer.phone_number if a.customer else None,
        service_id=str(a.service_id),
        service_name=a.service.name if a.service else None,
        staff_id=str(a.staff_id),
        staff_name=a.staff.name if a.staff else None,
        start_time=a.start_time,
        end_time=a.end_time,
        status=a.status.value if hasattr(a.status, "value") else str(a.status),
        notes=a.notes,
    )


@router.get("/", response_model=List[AppointmentResponse])
async def list_appointments(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    branch_id: str | None = None,
    staff_id: str | None = None,
    status: str | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
):
    """List appointments from PostgreSQL with filters."""
    stmt = (
        select(Appointment)
        .where(Appointment.business_id == UUID(business_id))
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
    )
    if branch_id:
        stmt = stmt.where(Appointment.branch_id == UUID(branch_id))
    if staff_id:
        stmt = stmt.where(Appointment.staff_id == UUID(staff_id))
    if status:
        stmt = stmt.where(Appointment.status == AppointmentStatus(status.lower()))
    if start_date:
        stmt = stmt.where(Appointment.start_time >= datetime.combine(start_date, time.min, tzinfo=timezone.utc))
    if end_date:
        stmt = stmt.where(Appointment.start_time <= datetime.combine(end_date, time.max, tzinfo=timezone.utc))

    stmt = stmt.order_by(Appointment.start_time.desc())
    res = await db.execute(stmt)
    return [_to_response(a) for a in res.scalars().all()]


@router.post("/", response_model=AppointmentResponse)
async def create_appointment(
    appointment: AppointmentCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create appointment in PostgreSQL."""
    biz_uuid = UUID(business_id)

    # Resolve branch
    branch_uuid = None
    if appointment.branch_id:
        try:
            branch_uuid = UUID(appointment.branch_id)
        except ValueError:
            pass
    if not branch_uuid:
        branch = (await db.execute(select(Branch).where(Branch.business_id == biz_uuid))).scalars().first()
        if not branch:
            branch = Branch(business_id=biz_uuid, name="Main Branch", timezone="Asia/Baku", is_active=True)
            db.add(branch)
            await db.flush()
        branch_uuid = branch.id

    # Resolve customer
    cust_uuid = None
    if appointment.customer_id:
        try:
            cust_uuid = UUID(appointment.customer_id)
        except ValueError:
            pass
    if not cust_uuid:
        phone = (appointment.customer_phone or "+994500000000").strip()
        cust = (
            await db.execute(
                select(Customer).where(Customer.business_id == biz_uuid, Customer.phone_number == phone)
            )
        ).scalar_one_or_none()
        if not cust:
            cust = Customer(
                business_id=biz_uuid,
                phone_number=phone,
                name=appointment.customer_name or "Walk-In Customer",
            )
            db.add(cust)
            await db.flush()
        cust_uuid = cust.id

    # Resolve service
    srv_uuid = UUID(appointment.service_id) if appointment.service_id else None
    if not srv_uuid:
        srv = (await db.execute(select(Service).where(Service.business_id == biz_uuid))).scalars().first()
        if not srv:
            raise HTTPException(status_code=400, detail="Please create at least one Service first")
        srv_uuid = srv.id

    # Resolve staff
    stf_uuid = UUID(appointment.staff_id) if appointment.staff_id else None
    if not stf_uuid:
        stf = (await db.execute(select(Staff).where(Staff.business_id == biz_uuid))).scalars().first()
        if not stf:
            raise HTTPException(status_code=400, detail="Please add at least one Staff member first")
        stf_uuid = stf.id

    end_time = appointment.end_time or datetime.fromtimestamp(
        appointment.start_time.timestamp() + 3600, tz=timezone.utc
    )

    new_appt = Appointment(
        business_id=biz_uuid,
        branch_id=branch_uuid,
        customer_id=cust_uuid,
        service_id=srv_uuid,
        staff_id=stf_uuid,
        start_time=appointment.start_time,
        end_time=end_time,
        status=AppointmentStatus.confirmed,
        source=AppointmentSource.staff_dashboard,
        notes=appointment.notes,
    )
    db.add(new_appt)
    await db.flush()

    stmt = (
        select(Appointment)
        .where(Appointment.id == new_appt.id)
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
    )
    loaded = (await db.execute(stmt)).scalar_one()
    return _to_response(loaded)


@router.get("/calendar", response_model=List[AppointmentResponse])
async def get_appointments_calendar(
    start_date: date,
    end_date: date,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    branch_id: str | None = None,
):
    """Get appointments for calendar view from PostgreSQL."""
    return await list_appointments(
        db=db,
        user=user,
        business_id=business_id,
        branch_id=branch_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get("/availability", response_model=List[AvailableSlot])
async def check_availability(
    service_id: str,
    target_date: date,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    staff_id: str | None = None,
):
    """Check available slots."""
    return []


@router.get("/my", response_model=List[AppointmentResponse])
async def get_my_appointments(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
):
    """Get appointments for the authenticated customer (Customer Mobile App)."""
    phone = user.get("phone") or user.get("sub") or ""
    stmt = (
        select(Appointment)
        .join(Customer, Appointment.customer_id == Customer.id)
        .where(Customer.phone_number == phone)
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
        .order_by(Appointment.start_time.desc())
    )
    res = await db.execute(stmt)
    return [_to_response(a) for a in res.scalars().all()]


@router.get("/{id}", response_model=AppointmentResponse)
async def get_appointment(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get appointment by ID."""
    stmt = (
        select(Appointment)
        .where(Appointment.id == UUID(id), Appointment.business_id == UUID(business_id))
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
    )
    appt = (await db.execute(stmt)).scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    return _to_response(appt)


@router.put("/{id}", response_model=AppointmentResponse)
@router.put("/{id}/status", response_model=AppointmentResponse)
async def update_appointment(
    id: str,
    update_data: AppointmentUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update appointment status or reschedule."""
    stmt = (
        select(Appointment)
        .where(Appointment.id == UUID(id), Appointment.business_id == UUID(business_id))
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
    )
    appt = (await db.execute(stmt)).scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")
    if update_data.status:
        appt.status = AppointmentStatus(update_data.status.lower())
    if update_data.start_time:
        appt.start_time = update_data.start_time
    if update_data.end_time:
        appt.end_time = update_data.end_time
    if update_data.staff_id:
        appt.staff_id = UUID(update_data.staff_id)
    if update_data.notes is not None:
        appt.notes = update_data.notes
    await db.flush()
    return _to_response(appt)
