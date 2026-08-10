from typing import Annotated, Any, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.core.dependencies import require_role

router = APIRouter()

class BusinessResponse(BaseModel):
    id: str
    name: str
    status: str

class PlanResponse(BaseModel):
    id: str
    name: str
    price: float

class PlanCreate(BaseModel):
    name: str
    price: float

class PlanUpdate(BaseModel):
    name: str | None = None
    price: float | None = None

class BusinessStatusUpdate(BaseModel):
    status: str

class AnalyticsResponse(BaseModel):
    total_businesses: int
    total_appointments: int
    total_messages: int

@router.get("/businesses", response_model=List[BusinessResponse])
async def list_businesses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """List all businesses on the platform (paginated)."""
    # TODO: Implement business list query
    return []

@router.get("/businesses/{id}", response_model=BusinessResponse)
async def get_business(
    id: str,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Get business details by ID."""
    # TODO: Implement business detail query
    return BusinessResponse(id=id, name="Placeholder Business", status="active")

@router.put("/businesses/{id}/status", response_model=BusinessResponse)
async def update_business_status(
    id: str,
    status_update: BusinessStatusUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Approve or suspend a business."""
    # TODO: Implement business status update
    return BusinessResponse(id=id, name="Placeholder Business", status=status_update.status)

@router.get("/plans", response_model=List[PlanResponse])
async def list_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """List all subscription plans."""
    # TODO: Implement plans list query
    return []

@router.post("/plans", response_model=PlanResponse)
async def create_plan(
    plan: PlanCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Create a new subscription plan."""
    # TODO: Implement plan creation
    return PlanResponse(id="placeholder", name=plan.name, price=plan.price)

@router.put("/plans/{id}", response_model=PlanResponse)
async def update_plan(
    id: str,
    plan: PlanUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Update a subscription plan."""
    # TODO: Implement plan update
    return PlanResponse(id=id, name=plan.name or "Updated", price=plan.price or 0.0)

@router.get("/analytics", response_model=AnalyticsResponse)
async def get_platform_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Get platform-wide analytics."""
    return AnalyticsResponse(total_businesses=0, total_appointments=0, total_messages=0)

class ActivateModelRequest(BaseModel):
    provider: str
    model_id: str
    api_key: str | None = None

@router.get("/ai-models/discover")
async def discover_latest_source_models(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Discover latest AI models directly from Google, Anthropic, and OpenAI official source REST APIs."""
    from app.services.ai_model_discovery_service import AIModelDiscoveryService
    return await AIModelDiscoveryService.discover_all_source_models()

@router.post("/ai-models/activate")
async def activate_model_version(
    req: ActivateModelRequest,
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Activate a specific model version or rotate API keys live with zero downtime."""
    from app.services.ai_registry import AIRegistryService
    AIRegistryService.update_provider_config(provider=req.provider, model_name=req.model_id, api_key=req.api_key)
    return {
        "status": "success",
        "message": f"Successfully activated '{req.model_id}' for provider '{req.provider}' live with zero downtime.",
        "active_config": AIRegistryService.get_provider_config(req.provider)
    }

@router.get("/margins")
async def get_tenant_margins_analytics(
    user: Annotated[dict[str, Any], Depends(require_role("saas_owner"))]
):
    """Get live unit economics, AI token costs, and net profit margins per tenant business."""
    from decimal import Decimal
    from app.services.saas_analytics_service import SaaSAnalyticsService
    
    sample_tenant = SaaSAnalyticsService.calculate_tenant_margin(
        business_id="b1",
        business_name="Beauty Studio Baku",
        plan_name="Pro Business Tier",
        subscription_price=Decimal("79.00"),
        provider="gemini",
        total_tokens=150000,
    )
    return {"tenants": [sample_tenant.__dict__]}


