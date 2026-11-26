from typing import Annotated, Any
from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException
from app.models.business import Business, BusinessOwner
from app.models.saas import SaasOwner
from app.models.reseller import Reseller

security = HTTPBearer()


def _try_uuid(value: Any) -> UUID | None:
    if not value:
        return None
    try:
        return UUID(str(value))
    except (ValueError, TypeError):
        return None


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> dict[str, Any]:
    """Decode JWT, extract validated user claims, and verify active status in DB."""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException(detail="Invalid token type")

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(detail="Could not validate credentials")

        role = payload.get("role")
        business_id = payload.get("business_id")
        reseller_id = payload.get("reseller_id")
        is_active = bool(payload.get("is_active", True))

        if role in {"owner", "business_owner", "staff"}:
            user_uuid = _try_uuid(user_id)
            if role in {"owner", "business_owner"} and user_uuid is not None:
                owner_row = (
                    await db.execute(select(BusinessOwner.is_active).where(BusinessOwner.id == user_uuid))
                ).scalar_one_or_none()
                if owner_row is not None and not owner_row:
                    raise ForbiddenException(detail="Account is disabled")
            biz_uuid = _try_uuid(business_id)
            if biz_uuid is not None:
                biz_active = (
                    await db.execute(select(Business.is_active).where(Business.id == biz_uuid))
                ).scalar_one_or_none()
                if biz_active is not None and not biz_active:
                    raise ForbiddenException(detail="Business account is disabled")
        elif role in {"saas_owner", "admin"}:
            saas_uuid = _try_uuid(user_id)
            if saas_uuid is not None:
                saas_active = (
                    await db.execute(select(SaasOwner.is_active).where(SaasOwner.id == saas_uuid))
                ).scalar_one_or_none()
                if saas_active is not None and not saas_active:
                    raise ForbiddenException(detail="Account is disabled")
        elif role == "reseller":
            res_uuid = _try_uuid(reseller_id) or _try_uuid(user_id)
            if res_uuid is not None:
                res_active = (
                    await db.execute(select(Reseller.is_active).where(Reseller.id == res_uuid))
                ).scalar_one_or_none()
                if res_active is not None and not res_active:
                    raise ForbiddenException(detail="Reseller account is disabled")

        return {
            "id": user_id,
            "email": payload.get("email"),
            "phone": payload.get("phone"),
            "role": role,
            "business_id": business_id,
            "reseller_id": reseller_id,
            "is_active": is_active,
        }
    except ValueError:
        raise UnauthorizedException(detail="Could not validate credentials")


def get_current_active_user(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)],
) -> dict[str, Any]:
    """Check if the current user is active."""
    if not current_user.get("is_active"):
        raise ForbiddenException(detail="Inactive user")
    return current_user


def require_role(*roles: str):
    """Return a dependency that checks if the user has one of the required roles.
    - 'owner' and 'business_owner' are treated interchangeably and inherit 'staff' permissions.
    - 'saas_owner' and 'admin' are treated interchangeably.
    """
    allowed_roles = set(roles)
    if "staff" in allowed_roles:
        allowed_roles.update({"owner", "business_owner", "saas_owner", "admin"})
    if "owner" in allowed_roles or "business_owner" in allowed_roles:
        allowed_roles.update({"owner", "business_owner", "saas_owner", "admin"})
    if "saas_owner" in allowed_roles or "admin" in allowed_roles:
        allowed_roles.update({"saas_owner", "admin"})

    def role_checker(
        current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
    ) -> dict[str, Any]:
        if current_user.get("role") not in allowed_roles:
            raise ForbiddenException(detail="Operation not permitted")
        return current_user

    return role_checker


def get_business_context(
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)],
) -> str:
    """Extract business_id from current user for tenant scoping."""
    business_id = current_user.get("business_id")
    if not business_id:
        raise ForbiddenException(detail="No business context available")
    return business_id
