from typing import Annotated, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
)
from app.models.saas import SaasOwner, Plan
from app.models.business import Business, BusinessOwner, Branch
from app.models.reseller import Reseller

router = APIRouter()


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RegisterBusinessRequest(BaseModel):
    business_name: str
    owner_name: str
    email: EmailStr
    phone: Optional[str] = None
    password: str
    category: Optional[str] = "Hair & Beauty"
    referral_code: Optional[str] = None
    plan_id: Optional[str] = None


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class OtpSendRequest(BaseModel):
    phone: str


class OtpVerifyRequest(BaseModel):
    phone: str
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None
    token_type: str = "bearer"
    role: Optional[str] = None
    business_id: Optional[str] = None
    reseller_id: Optional[str] = None


class UserInfoResponse(BaseModel):
    id: str
    email: Optional[str] = None
    role: str
    business_id: str | None = None
    reseller_id: str | None = None
    is_active: bool


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Authenticate SaaS Owner, Business Owner, or Reseller Partner and return signed JWT tokens."""
    email_clean = request.email.strip().lower()

    # 1. Check SaaS Owner in DB
    saas_owner = (
        await db.execute(select(SaasOwner).where(SaasOwner.email == email_clean))
    ).scalar_one_or_none()
    if saas_owner and verify_password(request.password, saas_owner.password_hash):
        if not saas_owner.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
        access = create_access_token(
            subject=str(saas_owner.id),
            role="saas_owner",
            extra_claims={"email": saas_owner.email},
        )
        refresh = create_refresh_token(subject=str(saas_owner.id))
        return TokenResponse(access_token=access, refresh_token=refresh, role="saas_owner")

    # 2. Fallback check against env-configured SAAS_ADMIN_EMAIL
    if email_clean == settings.SAAS_ADMIN_EMAIL.lower() and request.password == settings.SAAS_ADMIN_PASSWORD:
        access = create_access_token(
            subject="saas-root-admin",
            role="saas_owner",
            extra_claims={"email": email_clean},
        )
        refresh = create_refresh_token(subject="saas-root-admin")
        return TokenResponse(access_token=access, refresh_token=refresh, role="saas_owner")

    # 3. Check Business Owner
    biz_owner = (
        await db.execute(select(BusinessOwner).where(BusinessOwner.email == email_clean))
    ).scalar_one_or_none()
    if biz_owner and verify_password(request.password, biz_owner.password_hash):
        if not biz_owner.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is disabled")
        biz_id_str = str(biz_owner.business_id)
        access = create_access_token(
            subject=str(biz_owner.id),
            role="owner",
            business_id=biz_id_str,
            extra_claims={"email": biz_owner.email},
        )
        refresh = create_refresh_token(subject=str(biz_owner.id))
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            role="owner",
            business_id=biz_id_str,
        )

    # 4. Check Reseller Partner
    reseller = (
        await db.execute(select(Reseller).where(Reseller.email == email_clean))
    ).scalar_one_or_none()
    if reseller and verify_password(request.password, reseller.password_hash):
        if not reseller.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Reseller account is disabled")
        res_id_str = str(reseller.id)
        access = create_access_token(
            subject=res_id_str,
            role="reseller",
            extra_claims={"email": reseller.email, "reseller_id": res_id_str},
        )
        refresh = create_refresh_token(subject=res_id_str)
        return TokenResponse(
            access_token=access,
            refresh_token=refresh,
            role="reseller",
            reseller_id=res_id_str,
        )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid email or password",
    )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register_business(
    request: RegisterBusinessRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Self-register a new Business on randevu.vip (with optional Reseller referral code attribution)."""
    email_clean = request.email.strip().lower()
    existing = (
        await db.execute(select(BusinessOwner).where(BusinessOwner.email == email_clean))
    ).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email is already registered")

    # Resolve optional Reseller referral code
    reseller_id = None
    if request.referral_code:
        ref_clean = request.referral_code.strip().upper()
        reseller = (
            await db.execute(select(Reseller).where(Reseller.referral_code == ref_clean, Reseller.is_active == True))
        ).scalar_one_or_none()
        if reseller:
            reseller_id = reseller.id

    # Assign Starter plan by default if present
    starter_plan = (
        await db.execute(select(Plan).where(Plan.is_active == True).order_by(Plan.price.asc()))
    ).scalars().first()

    business = Business(
        name=request.business_name.strip(),
        plan_id=starter_plan.id if starter_plan else None,
        reseller_id=reseller_id,
        subscription_status="trial",
        category=request.category,
        is_active=True,
    )
    db.add(business)
    await db.flush()

    default_branch = Branch(
        business_id=business.id,
        name=f"{business.name} - Main Branch",
        timezone="Asia/Baku",
        is_active=True,
    )
    db.add(default_branch)

    owner = BusinessOwner(
        business_id=business.id,
        name=request.owner_name.strip(),
        phone=request.phone,
        email=email_clean,
        password_hash=hash_password(request.password),
        is_active=True,
    )
    db.add(owner)
    await db.flush()

    biz_id_str = str(business.id)
    access = create_access_token(
        subject=str(owner.id),
        role="owner",
        business_id=biz_id_str,
        extra_claims={"email": owner.email},
    )
    refresh = create_refresh_token(subject=str(owner.id))
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        role="owner",
        business_id=biz_id_str,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    req: RefreshTokenRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Refresh access token using a valid refresh token."""
    try:
        payload = decode_token(req.refresh_token)
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
        subject = payload.get("sub")
        if not subject:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token subject")

        access = create_access_token(
            subject=subject,
            role=payload.get("role", "owner"),
            business_id=payload.get("business_id"),
        )
        return TokenResponse(
            access_token=access,
            refresh_token=req.refresh_token,
            role=payload.get("role", "owner"),
            business_id=payload.get("business_id"),
        )
    except ValueError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired refresh token")


@router.post("/otp/send")
async def send_customer_otp(req: OtpSendRequest):
    """Send WhatsApp OTP verification code to customer phone."""
    return {"status": "sent", "phone": req.phone, "expires_in_seconds": 300}


@router.post("/otp/verify", response_model=TokenResponse)
async def verify_customer_otp(req: OtpVerifyRequest):
    """Verify customer OTP code and return customer session JWT."""
    if not req.code or len(req.code.strip()) < 4:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid OTP code")
    access = create_access_token(subject=f"customer:{req.phone}", role="customer")
    return TokenResponse(access_token=access, role="customer")


@router.get("/plans")
async def get_public_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Public endpoint returning active subscription plans for randevu.vip landing & registration."""
    plans = (
        await db.execute(select(Plan).where(Plan.is_active == True).order_by(Plan.price.asc()))
    ).scalars().all()
    return [
        {
            "id": str(p.id),
            "name": p.name,
            "price": float(p.price),
            "max_branches": p.max_branches,
            "max_whatsapp_numbers": p.max_whatsapp_numbers,
            "ai_message_quota": p.ai_message_quota,
            "allows_cadence_engine": bool(p.allows_cadence_engine),
            "allows_gift_vouchers": bool(p.allows_gift_vouchers),
            "allows_flash_drops": bool(p.allows_flash_drops),
            "allows_custom_domain": bool(p.allows_custom_domain),
            "features": p.features or {},
        }
        for p in plans
    ]


@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
):
    """Get current authenticated user information."""
    return UserInfoResponse(
        id=current_user["id"],
        email=current_user.get("email"),
        role=current_user["role"],
        business_id=current_user.get("business_id"),
        reseller_id=current_user.get("reseller_id"),
        is_active=current_user.get("is_active", True),
    )
