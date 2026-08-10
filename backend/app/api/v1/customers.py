from typing import Annotated, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context

router = APIRouter()

class CustomerBase(BaseModel):
    name: str
    phone: str
    email: str | None = None

class CustomerResponse(CustomerBase):
    id: str
    business_id: str

class CustomerDetailResponse(CustomerResponse):
    appointments: List[dict] = []

@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    q: str | None = Query(None, description="Search by name or phone"),
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)]
):
    """List customers, searchable by name/phone."""
    return []

@router.get("/discover")
async def discover_businesses(
    category: str | None = Query(None, description="Filter by business category"),
    q: str | None = Query(None, description="Search query"),
    db: Annotated[AsyncSession, Depends(get_db)] = None,
):
    """Public / Customer discovery endpoint returning discoverable businesses."""
    return [
        {
            "id": "b1",
            "name": "Beauty Studio Baku",
            "category": "Hair & Beauty",
            "description": "Premium hair salon in Central Baku",
            "logo_url": "https://example.com/logo.png",
            "is_discoverable": True,
            "branches": [
                {"id": "br1", "name": "Central Branch", "location": "Nizami St 42", "latitude": 40.3772, "longitude": 49.8541}
            ]
        }
    ]

