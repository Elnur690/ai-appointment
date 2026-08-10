from typing import Annotated, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class BranchBase(BaseModel):
    name: str
    address: str | None = None
    phone: str | None = None

class BranchCreate(BranchBase):
    pass

class BranchUpdate(BaseModel):
    name: str | None = None
    address: str | None = None
    phone: str | None = None

class BranchResponse(BranchBase):
    id: str
    business_id: str
    is_active: bool

class WhatsAppStatusResponse(BaseModel):
    status: str
    connected: bool

@router.get("/", response_model=List[BranchResponse])
async def list_branches(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List all branches for the current business."""
    # TODO: Implement branch list
    return []

@router.post("/", response_model=BranchResponse)
async def create_branch(
    branch: BranchCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Create a new branch."""
    # TODO: Implement branch creation
    return BranchResponse(id="temp", business_id=business_id, name=branch.name, is_active=True)

@router.get("/{id}", response_model=BranchResponse)
async def get_branch(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get a specific branch by ID."""
    # TODO: Implement branch fetch
    return BranchResponse(id=id, business_id=business_id, name="Placeholder", is_active=True)

@router.put("/{id}", response_model=BranchResponse)
async def update_branch(
    id: str,
    branch_update: BranchUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Update a specific branch."""
    # TODO: Implement branch update
    return BranchResponse(id=id, business_id=business_id, name=branch_update.name or "Updated", is_active=True)

@router.get("/{id}/whatsapp-status", response_model=WhatsAppStatusResponse)
async def get_whatsapp_status(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """Get WhatsApp connection status for a branch."""
    # TODO: Check evolution API status
    return WhatsAppStatusResponse(status="disconnected", connected=False)
