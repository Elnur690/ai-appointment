from datetime import date, datetime, time, timezone
from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, Response
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


def _parse_uuid(val: str, field: str = "id") -> UUID:
    try:
        return UUID(str(val))
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid {field}")


async def _assert_no_staff_overlap(
    db: AsyncSession,
    biz_uuid: UUID,
    staff_uuid: UUID,
    start_time: datetime,
    end_time: datetime,
    exclude_appointment_id: UUID | None = None,
) -> None:
    stmt = select(Appointment.id).where(
        Appointment.business_id == biz_uuid,
        Appointment.staff_id == staff_uuid,
        Appointment.status != AppointmentStatus.cancelled,
        Appointment.start_time < end_time,
        Appointment.end_time > start_time,
    )
    if exclude_appointment_id is not None:
        stmt = stmt.where(Appointment.id != exclude_appointment_id)
    conflict = (await db.execute(stmt.limit(1))).scalar_one_or_none()
    if conflict is not None:
        raise HTTPException(
            status_code=409,
            detail="Staff member already has an overlapping appointment in this time slot",
        )


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
        stmt = stmt.where(Appointment.branch_id == _parse_uuid(branch_id, "branch_id"))
    if staff_id:
        stmt = stmt.where(Appointment.staff_id == _parse_uuid(staff_id, "staff_id"))
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
        branch_uuid = _parse_uuid(appointment.branch_id, "branch_id")
        branch_exists = (
            await db.execute(select(Branch.id).where(Branch.id == branch_uuid, Branch.business_id == biz_uuid))
        ).scalar_one_or_none()
        if not branch_exists:
            raise HTTPException(status_code=404, detail="Branch not found")
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
        cust_uuid = _parse_uuid(appointment.customer_id, "customer_id")
        cust_exists = (
            await db.execute(select(Customer.id).where(Customer.id == cust_uuid, Customer.business_id == biz_uuid))
        ).scalar_one_or_none()
        if not cust_exists:
            raise HTTPException(status_code=404, detail="Customer not found")
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
    srv_uuid = None
    if appointment.service_id:
        srv_uuid = _parse_uuid(appointment.service_id, "service_id")
        srv_exists = (
            await db.execute(select(Service.id).where(Service.id == srv_uuid, Service.business_id == biz_uuid))
        ).scalar_one_or_none()
        if not srv_exists:
            raise HTTPException(status_code=404, detail="Service not found")
    if not srv_uuid:
        srv = (await db.execute(select(Service).where(Service.business_id == biz_uuid))).scalars().first()
        if not srv:
            raise HTTPException(status_code=400, detail="Please create at least one Service first")
        srv_uuid = srv.id

    # Resolve staff
    stf_uuid = None
    if appointment.staff_id:
        stf_uuid = _parse_uuid(appointment.staff_id, "staff_id")
        stf_exists = (
            await db.execute(select(Staff.id).where(Staff.id == stf_uuid, Staff.business_id == biz_uuid))
        ).scalar_one_or_none()
        if not stf_exists:
            raise HTTPException(status_code=404, detail="Staff member not found")
    if not stf_uuid:
        stf = (await db.execute(select(Staff).where(Staff.business_id == biz_uuid))).scalars().first()
        if not stf:
            raise HTTPException(status_code=400, detail="Please add at least one Staff member first")
        stf_uuid = stf.id

    end_time = appointment.end_time or datetime.fromtimestamp(
        appointment.start_time.timestamp() + 3600, tz=timezone.utc
    )

    await _assert_no_staff_overlap(db, biz_uuid, stf_uuid, appointment.start_time, end_time)

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


@router.get("/ical-feed")
async def export_ical_feed(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: str | None = Query(None),
):
    """Export upcoming business appointments as an iCalendar (.ics) feed for Google & Apple Calendar."""
    caller_biz_id = user.get("business_id")
    target_biz_id = business_id or caller_biz_id
    if not target_biz_id:
        raise HTTPException(status_code=400, detail="business_id is required")
    if user.get("role") not in {"saas_owner", "admin"} and str(target_biz_id) != str(caller_biz_id or ""):
        raise HTTPException(status_code=403, detail="Not authorized to access this business calendar")
    biz_uuid = _parse_uuid(str(target_biz_id), "business_id")

    stmt = (
        select(Appointment)
        .where(
            Appointment.business_id == biz_uuid,
            Appointment.status.notin_([AppointmentStatus.cancelled]),
        )
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
        .order_by(Appointment.start_time.asc())
        .limit(200)
    )
    rows = (await db.execute(stmt)).scalars().all()
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Randevu.vip//AI Appointment Calendar//EN",
        "CALSCALE:GREGORIAN",
        "X-WR-CALNAME:Randevu.vip Appointments",
    ]
    for a in rows:
        dt_start = a.start_time.strftime("%Y%m%dT%H%M%SZ")
        dt_end = a.end_time.strftime("%Y%m%dT%H%M%SZ")
        svc_name = a.service.name if a.service else "Appointment"
        cust_name = (a.customer.name or a.customer.phone_number) if a.customer else "Client"
        staff_name = a.staff.name if a.staff else "Staff"
        lines.extend([
            "BEGIN:VEVENT",
            f"UID:{a.id}@randevu.vip",
            f"DTSTART:{dt_start}",
            f"DTEND:{dt_end}",
            f"SUMMARY:{svc_name} - {cust_name}",
            f"DESCRIPTION:Staff: {staff_name} | Status: {a.status.value}",
            "END:VEVENT",
        ])
    lines.append("END:VCALENDAR")
    return Response(content="\r\n".join(lines), media_type="text/calendar")


@router.get("/my", response_model=List[AppointmentResponse])
async def get_my_appointments(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
):
    """Get appointments for the authenticated customer (Customer Mobile App)."""
    raw_phone = user.get("phone") or user.get("sub") or user.get("id") or ""
    phone = str(raw_phone).removeprefix("customer:").strip()
    if not phone:
        return []
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
    appt_uuid = _parse_uuid(id, "appointment_id")
    stmt = (
        select(Appointment)
        .where(Appointment.id == appt_uuid, Appointment.business_id == UUID(business_id))
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
    biz_uuid = UUID(business_id)
    appt_uuid = _parse_uuid(id, "appointment_id")
    stmt = (
        select(Appointment)
        .where(Appointment.id == appt_uuid, Appointment.business_id == biz_uuid)
        .options(
            selectinload(Appointment.customer),
            selectinload(Appointment.service),
            selectinload(Appointment.staff),
        )
    )
    appt = (await db.execute(stmt)).scalar_one_or_none()
    if not appt:
        raise HTTPException(status_code=404, detail="Appointment not found")

    new_status = AppointmentStatus(update_data.status.lower()) if update_data.status else appt.status
    new_start = update_data.start_time or appt.start_time
    new_end = update_data.end_time or appt.end_time
    new_staff_uuid = appt.staff_id
    if update_data.staff_id:
        new_staff_uuid = _parse_uuid(update_data.staff_id, "staff_id")
        stf_exists = (
            await db.execute(select(Staff.id).where(Staff.id == new_staff_uuid, Staff.business_id == biz_uuid))
        ).scalar_one_or_none()
        if not stf_exists:
            raise HTTPException(status_code=404, detail="Staff member not found")

    if new_status != AppointmentStatus.cancelled and (
        update_data.start_time is not None
        or update_data.end_time is not None
        or update_data.staff_id is not None
        or appt.status == AppointmentStatus.cancelled
    ):
        await _assert_no_staff_overlap(
            db, biz_uuid, new_staff_uuid, new_start, new_end, exclude_appointment_id=appt.id
        )

    if update_data.status:
        appt.status = new_status
    if update_data.start_time:
        appt.start_time = new_start
    if update_data.end_time:
        appt.end_time = new_end
    if update_data.staff_id:
        appt.staff_id = new_staff_uuid
    if update_data.notes is not None:
        appt.notes = update_data.notes
    await db.flush()
    return _to_response(appt)
