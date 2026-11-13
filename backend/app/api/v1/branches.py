from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.business import Branch

router = APIRouter()


class BranchBase(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class BranchCreate(BranchBase):
    pass


class BranchUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class BranchResponse(BranchBase):
    id: str
    business_id: str
    is_active: bool


class WhatsAppStatusResponse(BaseModel):
    status: str
    connected: bool


def _to_response(b: Branch) -> BranchResponse:
    return BranchResponse(
        id=str(b.id),
        business_id=str(b.business_id),
        name=b.name,
        address=b.location,
        phone=b.phone,
        latitude=b.latitude,
        longitude=b.longitude,
        is_active=bool(b.is_active),
    )


@router.get("/", response_model=List[BranchResponse])
async def list_branches(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """List all branches for the current business from PostgreSQL."""
    stmt = select(Branch).where(Branch.business_id == UUID(business_id)).order_by(Branch.created_at.asc())
    res = await db.execute(stmt)
    return [_to_response(b) for b in res.scalars().all()]


@router.post("/", response_model=BranchResponse)
async def create_branch(
    branch: BranchCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create a new branch in PostgreSQL."""
    new_branch = Branch(
        business_id=UUID(business_id),
        name=branch.name.strip(),
        location=branch.address,
        phone=branch.phone,
        latitude=branch.latitude,
        longitude=branch.longitude,
        is_active=True,
    )
    db.add(new_branch)
    await db.flush()
    return _to_response(new_branch)


@router.get("/{id}", response_model=BranchResponse)
async def get_branch(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get a specific branch by ID."""
    stmt = select(Branch).where(Branch.id == UUID(id), Branch.business_id == UUID(business_id))
    b = (await db.execute(stmt)).scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Branch not found")
    return _to_response(b)


@router.put("/{id}", response_model=BranchResponse)
async def update_branch(
    id: str,
    branch_update: BranchUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update a specific branch."""
    stmt = select(Branch).where(Branch.id == UUID(id), Branch.business_id == UUID(business_id))
    b = (await db.execute(stmt)).scalar_one_or_none()
    if not b:
        raise HTTPException(status_code=404, detail="Branch not found")
    for k, v in branch_update.model_dump(exclude_unset=True).items():
        if k == "address":
            b.location = v
        elif hasattr(b, k):
            setattr(b, k, v)
    await db.flush()
    return _to_response(b)


@router.get("/{id}/whatsapp-status", response_model=WhatsAppStatusResponse)
async def get_whatsapp_status(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get WhatsApp connection status for a branch."""
    stmt = select(Branch).where(Branch.id == UUID(id), Branch.business_id == UUID(business_id))
    b = (await db.execute(stmt)).scalar_one_or_none()
    connected = bool(b and b.whatsapp_instance_id)
    return WhatsAppStatusResponse(
        status="connected" if connected else "disconnected",
        connected=connected,
    )
