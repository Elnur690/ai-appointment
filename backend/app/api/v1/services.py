from typing import Annotated, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class ServiceBase(BaseModel):
    name: str
    description: str | None = None
    duration_minutes: int
    price: float

class ServiceCreate(ServiceBase):
    pass

class ServiceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    duration_minutes: int | None = None
    price: float | None = None

class ServiceResponse(ServiceBase):
    id: str
    business_id: str
    is_active: bool

@router.get("/", response_model=List[ServiceResponse])
async def list_services(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List services for the business."""
    return []

@router.post("/", response_model=ServiceResponse)
async def create_service(
    service: ServiceCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Create a new service."""
    return ServiceResponse(id="temp", business_id=business_id, **service.model_dump(), is_active=True)

@router.get("/{id}", response_model=ServiceResponse)
async def get_service(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get a service by ID."""
    return ServiceResponse(id=id, business_id=business_id, name="Placeholder", duration_minutes=30, price=0.0, is_active=True)

@router.put("/{id}", response_model=ServiceResponse)
async def update_service(
    id: str,
    service_update: ServiceUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Update a service."""
    return ServiceResponse(id=id, business_id=business_id, name="Updated", duration_minutes=30, price=0.0, is_active=True)

@router.delete("/{id}")
async def deactivate_service(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Deactivate a service."""
    return {"status": "success"}
