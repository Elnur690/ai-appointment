import base64
from typing import Annotated, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import require_role, get_business_context
from app.models.business import Business, Branch
from app.models.appointment import Appointment
from app.models.payment import Payment
from app.services.custom_domain_service import CustomDomainService
from app.integrations.whatsapp.client import EvolutionAPIClient

router = APIRouter()


class BusinessResponse(BaseModel):
    id: str
    name: str
    custom_domain: Optional[str] = None
    reseller_id: Optional[str] = None
    settings: dict = {}


class BusinessUpdate(BaseModel):
    name: str | None = None
    custom_domain: str | None = None
    settings: dict | None = None


class BusinessAnalyticsResponse(BaseModel):
    appointments_this_month: int
    revenue_this_month: float


class CustomDomainVerifyRequest(BaseModel):
    custom_domain: str


def _parse_uuid_safe(val: str) -> Optional[UUID]:
    try:
        return UUID(str(val))
    except (ValueError, TypeError):
        return None


@router.get("/", response_model=BusinessResponse)
async def get_own_business(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get details of the currently authenticated business."""
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
        if biz:
            return BusinessResponse(
                id=str(biz.id),
                name=biz.name,
                custom_domain=biz.custom_domain,
                reseller_id=str(biz.reseller_id) if biz.reseller_id else None,
                settings=biz.default_ai_tone_config or {},
            )
    return BusinessResponse(id=business_id, name="My Business")


@router.put("/", response_model=BusinessResponse)
async def update_own_business(
    update_data: BusinessUpdate,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Update settings of the currently authenticated business."""
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
        if biz:
            if update_data.name is not None:
                biz.name = update_data.name
            if update_data.custom_domain is not None:
                biz.custom_domain = update_data.custom_domain.strip().lower()
            if update_data.settings is not None:
                biz.default_ai_tone_config = update_data.settings
            await db.flush()
            return BusinessResponse(
                id=str(biz.id),
                name=biz.name,
                custom_domain=biz.custom_domain,
                reseller_id=str(biz.reseller_id) if biz.reseller_id else None,
                settings=biz.default_ai_tone_config or {},
            )
    return BusinessResponse(
        id=business_id,
        name=update_data.name or "My Business",
        custom_domain=update_data.custom_domain,
        settings=update_data.settings or {},
    )


@router.get("/analytics", response_model=BusinessAnalyticsResponse)
async def get_business_analytics(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Get analytics for the current business."""
    biz_uuid = _parse_uuid_safe(business_id)
    if biz_uuid:
        appt_count = (
            await db.execute(select(func.count(Appointment.id)).where(Appointment.business_id == biz_uuid))
        ).scalar_one()
        rev_sum = (
            await db.execute(select(func.coalesce(func.sum(Payment.amount), 0)).where(Payment.business_id == biz_uuid))
        ).scalar_one()
        return BusinessAnalyticsResponse(
            appointments_this_month=int(appt_count or 0),
            revenue_this_month=float(rev_sum or 0.0),
        )
    return BusinessAnalyticsResponse(appointments_this_month=0, revenue_this_month=0.0)


@router.post("/custom-domain/verify")
async def verify_business_custom_domain(
    req: CustomDomainVerifyRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
):
    """Verify CNAME pointing to cname.randevu.vip and provision SSL."""
    biz_uuid = _parse_uuid_safe(business_id) or UUID("00000000-0000-0000-0000-000000000001")
    service = CustomDomainService()
    status_res = await service.verify_and_provision_cname(req.custom_domain, biz_uuid)
    if _parse_uuid_safe(business_id):
        biz = (await db.execute(select(Business).where(Business.id == biz_uuid))).scalar_one_or_none()
        if biz:
            biz.custom_domain = status_res.custom_domain
            await db.flush()
    return status_res.__dict__


@router.get("/whatsapp/qr-code")
async def get_whatsapp_pairing_qr(
    db: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[dict[str, Any], Depends(require_role("owner"))],
    business_id: Annotated[str, Depends(get_business_context)],
    branch_id: Optional[str] = None,
):
    """Proxy WhatsApp QR code generation and status from internal Evolution API container."""
    instance_name = f"randevu_{business_id[:8]}_{branch_id[:8] if branch_id else 'main'}"
    evo_client = EvolutionAPIClient(
        base_url=settings.EVOLUTION_API_URL,
        api_key=settings.EVOLUTION_API_KEY,
    )
    try:
        try:
            state_res = await evo_client.get_instance_status(instance_name)
            conn_state = (
                state_res.get("instance", {}).get("state")
                or state_res.get("state")
                or ""
            )
            if conn_state == "open":
                await evo_client.close()
                return {
                    "instance_name": instance_name,
                    "status": "connected",
                    "qr_code_data_url": None,
                    "source": "evolution_api_internal",
                }
        except Exception:
            await evo_client.create_instance(
                instance_name,
                webhook_url="http://backend:22800/api/v1/webhooks/whatsapp",
            )

        connect_res = await evo_client.connect_instance(instance_name)
        await evo_client.close()
        qr_base64 = connect_res.get("base64") or connect_res.get("qrcode", {}).get("base64")
        if qr_base64:
            return {
                "instance_name": instance_name,
                "status": "pairing",
                "qr_code_data_url": qr_base64,
                "source": "evolution_api_internal",
            }
        return {
            "instance_name": instance_name,
            "status": connect_res.get("instance", {}).get("state", "initializing"),
            "qr_code_data_url": None,
            "source": "evolution_api_internal",
        }
    except Exception as exc:
        await evo_client.close()
        return {
            "instance_name": instance_name,
            "status": "unavailable",
            "qr_code_data_url": None,
            "detail": str(exc),
            "source": "evolution_api_internal",
        }
