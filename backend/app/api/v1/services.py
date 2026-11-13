from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.business import Branch
from app.models.service import Service

router = APIRouter()


class ServiceBase(BaseModel):
    name: str
    description: str | None = None
    duration_minutes: int
    price: float
    currency: str = "AZN"
    buffer_minutes: int = 0
    branch_id: str | None = None


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    price: float | None = None
    buffer_minutes: int | None = None
    is_active: bool | None = None


class ServiceResponse(ServiceBase):
    id: str
    business_id: str
    is_active: bool


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


def _to_response(s: Service) -> ServiceResponse:
    return ServiceResponse(
        id=str(s.id),
        business_id=str(s.business_id),
        branch_id=str(s.branch_id),
        name=s.name,
        description=s.description,
        duration_minutes=int(s.duration_minutes),
        price=float(s.price),
        currency=s.currency or "AZN",
        buffer_minutes=int(s.buffer_minutes or 0),
        is_active=bool(s.is_active),
    )


@router.get("/", response_model=List[ServiceResponse])
async def list_services(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """List services for the business from PostgreSQL."""
    stmt = select(Service).where(Service.business_id == UUID(business_id)).order_by(Service.created_at.asc())
    res = await db.execute(stmt)
    return [_to_response(s) for s in res.scalars().all()]


@router.post("/", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create a new service in PostgreSQL."""
    biz_uuid = UUID(business_id)
    branch_uuid = await _resolve_branch_id(db, biz_uuid, service.branch_id)
    new_service = Service(
        business_id=biz_uuid,
        branch_id=branch_uuid,
        name=service.name.strip(),
        description=service.description,
        duration_minutes=service.duration_minutes,
        price=service.price,
        currency=service.currency or "AZN",
        buffer_minutes=service.buffer_minutes or 0,
        is_active=True,
    )
    db.add(new_service)
    await db.flush()
    return _to_response(new_service)


@router.get("/{id}", response_model=ServiceResponse)
async def get_service(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get a service by ID."""
    stmt = select(Service).where(Service.id == UUID(id), Service.business_id == UUID(business_id))
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    return _to_response(s)


@router.put("/{id}", response_model=ServiceResponse)
async def update_service(
    id: str,
    service_update: ServiceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update a service."""
    stmt = select(Service).where(Service.id == UUID(id), Service.business_id == UUID(business_id))
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    for k, v in service_update.model_dump(exclude_unset=True).items():
        if hasattr(s, k):
            setattr(s, k, v)
    await db.flush()
    return _to_response(s)


@router.delete("/{id}")
async def deactivate_service(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Deactivate a service."""
    stmt = select(Service).where(Service.id == UUID(id), Service.business_id == UUID(business_id))
    s = (await db.execute(stmt)).scalar_one_or_none()
    if not s:
        raise HTTPException(status_code=404, detail="Service not found")
    s.is_active = False
    await db.flush()
    return {"status": "success"}
