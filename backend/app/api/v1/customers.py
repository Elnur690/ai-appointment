from typing import Annotated, Any, List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import get_current_active_user, get_business_context
from app.models.business import Business
from app.models.customer import Customer

router = APIRouter()


class CustomerCreate(BaseModel):
    phone: str
    name: str | None = None
    email: str | None = None
    language_pref: str = "az"


class CustomerResponse(BaseModel):
    id: str
    business_id: str
    phone: str
    name: str | None = None
    email: str | None = None
    visits: int = 0
    tier: str = "Standard"
    language_pref: str = "az"


class CustomerDetailResponse(CustomerResponse):
    appointments: List[dict] = []


def _to_response(c: Customer, visits: int = 0) -> CustomerResponse:
    tier = "VIP Gold" if visits >= 10 else ("Silver" if visits >= 5 else "Standard")
    return CustomerResponse(
        id=str(c.id),
        business_id=str(c.business_id),
        phone=c.phone_number,
        name=c.name or c.phone_number,
        email=None,
        visits=visits,
        tier=tier,
        language_pref=c.language_pref or "az",
    )


@router.get("/", response_model=List[CustomerResponse])
async def list_customers(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
    q: str | None = Query(None, description="Search by name or phone"),
):
    """List customers from PostgreSQL, searchable by name/phone."""
    from sqlalchemy.orm import selectinload
    stmt = (
        select(Customer)
        .where(Customer.business_id == UUID(business_id))
        .options(selectinload(Customer.appointments))
    )
    if q:
        pattern = f"%{q.strip()}%"
        stmt = stmt.where(or_(Customer.name.ilike(pattern), Customer.phone_number.ilike(pattern)))
    stmt = stmt.order_by(Customer.created_at.desc())
    res = await db.execute(stmt)
    return [_to_response(c, visits=len(c.appointments or [])) for c in res.scalars().all()]


@router.post("/", response_model=CustomerResponse)
async def create_customer(
    payload: CustomerCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Create a customer in PostgreSQL."""
    cust = Customer(
        business_id=UUID(business_id),
        phone_number=payload.phone.strip(),
        name=payload.name.strip() if payload.name else None,
        language_pref=payload.language_pref or "az",
    )
    db.add(cust)
    await db.flush()
    return _to_response(cust)


@router.get("/discover")
async def discover_businesses(
    db: Annotated[AsyncSession, Depends(get_db)],
    category: str | None = Query(None, description="Filter by business category"),
    q: str | None = Query(None, description="Search query"),
):
    """Public / Customer discovery endpoint returning real active businesses from PostgreSQL."""
    stmt = select(Business).where(Business.is_active == True)
    if category and category != "All":
        stmt = stmt.where(Business.category == category)
    if q:
        stmt = stmt.where(Business.name.ilike(f"%{q.strip()}%"))
    stmt = stmt.order_by(Business.created_at.desc())
    res = await db.execute(stmt)
    return [
        {
            "id": str(b.id),
            "name": b.name,
            "category": b.category or "General",
            "description": b.description or "",
            "logo_url": b.logo_url,
            "custom_domain": b.custom_domain,
        }
        for b in res.scalars().all()
    ]


@router.get("/{id}", response_model=CustomerDetailResponse)
async def get_customer(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get customer details & appointment history from PostgreSQL."""
    stmt = select(Customer).where(Customer.id == UUID(id), Customer.business_id == UUID(business_id))
    c = (await db.execute(stmt)).scalar_one_or_none()
    if not c:
        raise HTTPException(status_code=404, detail="Customer not found")
    return CustomerDetailResponse(
        id=str(c.id),
        business_id=str(c.business_id),
        phone=c.phone_number,
        name=c.name,
        language_pref=c.language_pref or "az",
        appointments=[],
    )
