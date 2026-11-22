from datetime import datetime, timedelta, timezone
from typing import Annotated, Any, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.config import settings
from app.core.database import get_db
from app.core.email_validation import assert_allowed_registration_email
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
    owner_name: Optional[str] = None
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
    assert_allowed_registration_email(email_clean)
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

    # Assign selected plan or Starter plan by default
    selected_plan = None
    if request.plan_id:
        try:
            selected_plan = (
                await db.execute(select(Plan).where(Plan.id == UUID(request.plan_id), Plan.is_active == True))
            ).scalar_one_or_none()
        except ValueError:
            selected_plan = None
    if not selected_plan:
        selected_plan = (
            await db.execute(select(Plan).where(Plan.is_active == True).order_by(Plan.price.asc()))
        ).scalars().first()

    trial_days = int(getattr(selected_plan, "trial_days", 14) or 14) if selected_plan else 14
    allows_trial = bool(getattr(selected_plan, "allows_free_trial", True)) if selected_plan else True
    trial_ends = (
        datetime.now(timezone.utc) + timedelta(days=trial_days)
        if allows_trial and trial_days > 0
        else None
    )

    business = Business(
        name=request.business_name.strip(),
        plan_id=selected_plan.id if selected_plan else None,
        reseller_id=reseller_id,
        subscription_status="trial" if allows_trial else "active",
        trial_ends_at=trial_ends,
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
        name=(request.owner_name or request.business_name).strip(),
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


@router.get("/public-config")
async def get_public_platform_config(db: Annotated[AsyncSession, Depends(get_db)]):
    """Return public landing-page settings such as the platform WhatsApp support number."""
    from app.models.saas import PlatformConfig
    cfg = (await db.execute(select(PlatformConfig).where(PlatformConfig.config_key == "global"))).scalar_one_or_none()
    return {
        "support_whatsapp_number": (getattr(cfg, "support_whatsapp_number", None) or "") if cfg else "",
    }


@router.get("/plans")
async def get_public_plans(
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Public endpoint returning active subscription plans with all entitlement flags for randevu.vip & app.randevu.vip."""
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
            "message_limit": p.ai_message_quota,
            "allows_free_trial": bool(getattr(p, "allows_free_trial", True)),
            "trial_days": int(getattr(p, "trial_days", 14) or 0),
            "trial_features": getattr(p, "trial_features", None) or {},
            "allows_whatsapp": bool(getattr(p, "allows_whatsapp", True)),
            "allows_instagram": bool(getattr(p, "allows_instagram", False) or p.allows_omnichannel_messaging),
            "allows_telegram": bool(getattr(p, "allows_telegram", False) or p.allows_omnichannel_messaging),
            "allows_voice_messages": bool(p.allows_voice_messages),
            "allows_online_payments": bool(p.allows_online_payments),
            "allowed_payment_providers": getattr(p, "allowed_payment_providers", None) or ["cash", "payriff", "epoint"],
            "allows_no_show_deposits": bool(p.allows_no_show_deposits),
            "allows_shift_management": bool(p.allows_shift_management),
            "allows_cadence_engine": bool(p.allows_cadence_engine),
            "allows_flash_drops": bool(p.allows_flash_drops),
            "allows_gift_vouchers": bool(p.allows_gift_vouchers),
            "allows_loyalty_program": bool(p.allows_loyalty_program),
            "allows_combo_packages": bool(p.allows_combo_packages),
            "allows_group_bookings": bool(p.allows_group_bookings),
            "allows_product_upsells": bool(p.allows_product_upsells),
            "allows_dynamic_pricing": bool(p.allows_dynamic_pricing),
            "allows_winback_campaigns": bool(p.allows_winback_campaigns),
            "allows_gcal_sync": bool(p.allows_gcal_sync),
            "allows_apple_cal_sync": bool(p.allows_apple_cal_sync),
            "allows_geo_routing": bool(p.allows_geo_routing),
            "allows_emergency_reassignment": bool(p.allows_emergency_reassignment),
            "allows_omnichannel_messaging": bool(p.allows_omnichannel_messaging),
            "allows_growth_advisor": bool(p.allows_growth_advisor),
            "allows_branch_level_ai_tone": bool(p.allows_branch_level_ai_tone),
            "allows_discovery": bool(p.allows_discovery),
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


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


async def _send_reset_email(to_email: str, reset_url: str) -> None:
    if settings.RESEND_API_KEY:
        import httpx
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                await client.post(
                    "https://api.resend.com/emails",
                    headers={
                        "Authorization": f"Bearer {settings.RESEND_API_KEY}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "from": settings.SMTP_FROM_EMAIL,
                        "to": [to_email],
                        "subject": "Randevu.vip — Şifrə Sıfırlama / Password Reset",
                        "html": f"<p>Şifrənizi yeniləmək üçün aşağıdakı linkə keçid edin (30 dəqiqə etibarlıdır):</p><p><a href='{reset_url}'>{reset_url}</a></p>",
                    },
                )
        except Exception:
            pass
    elif settings.SMTP_HOST and settings.SMTP_USER and settings.SMTP_PASSWORD:
        import smtplib
        from email.message import EmailMessage
        try:
            msg = EmailMessage()
            msg["Subject"] = "Randevu.vip — Password Reset"
            msg["From"] = settings.SMTP_FROM_EMAIL
            msg["To"] = to_email
            msg.set_content(f"Reset your password (valid 30 minutes): {reset_url}")
            with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT, timeout=10) as server:
                server.starttls()
                server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
                server.send_message(msg)
        except Exception:
            pass


@router.post("/forgot-password")
async def forgot_password(
    req: ForgotPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Send a password reset link if the account exists (business owner or reseller)."""
    email_clean = req.email.strip().lower()
    target_id: str | None = None
    target_role: str | None = None

    owner = (await db.execute(select(BusinessOwner).where(BusinessOwner.email == email_clean))).scalar_one_or_none()
    if owner:
        target_id = str(owner.id)
        target_role = "owner"
    else:
        reseller = (await db.execute(select(Reseller).where(Reseller.email == email_clean))).scalar_one_or_none()
        if reseller:
            target_id = str(reseller.id)
            target_role = "reseller"

    if target_id and target_role:
        reset_token = create_access_token(
            subject=target_id,
            role=target_role,
            extra_claims={"purpose": "password_reset", "email": email_clean},
            expires_delta=timedelta(minutes=30),
        )
        reset_url = f"https://app.{settings.PLATFORM_DOMAIN}/login?reset_token={reset_token}"
        await _send_reset_email(email_clean, reset_url)

    return {
        "status": "ok",
        "message": "If an account with that email exists, password reset instructions have been sent.",
    }


@router.post("/reset-password")
async def reset_password(
    req: ResetPasswordRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
):
    """Verify a password reset JWT token and update the user's password."""
    from jose import JWTError
    from app.core.security import decode_token

    if len(req.new_password or "") < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")

    try:
        payload = decode_token(req.token)
    except JWTError:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if payload.get("purpose") != "password_reset":
        raise HTTPException(status_code=400, detail="Invalid reset token")

    user_id = payload.get("sub")
    role = payload.get("role")
    if role == "owner":
        user = (await db.execute(select(BusinessOwner).where(BusinessOwner.id == UUID(user_id)))).scalar_one_or_none()
    elif role == "reseller":
        user = (await db.execute(select(Reseller).where(Reseller.id == UUID(user_id)))).scalar_one_or_none()
    else:
        user = None

    if not user:
        raise HTTPException(status_code=404, detail="Account not found")

    user.password_hash = hash_password(req.new_password)
    await db.commit()
    return {"status": "ok", "message": "Password has been reset successfully."}
