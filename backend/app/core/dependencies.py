from typing import Annotated, Any
from fastapi import Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_token
from app.core.exceptions import UnauthorizedException, ForbiddenException

security = HTTPBearer()

async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
    db: Annotated[AsyncSession, Depends(get_db)]
) -> dict[str, Any]:
    """Decode JWT and get user details. Returns a placeholder dict for now."""
    try:
        payload = decode_token(credentials.credentials)
        if payload.get("type") != "access":
            raise UnauthorizedException(detail="Invalid token type")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise UnauthorizedException(detail="Could not validate credentials")
            
        # TODO: Load user from database using user_id
        # For now, returning a dict with token claims
        return {
            "id": user_id,
            "role": payload.get("role"),
            "business_id": payload.get("business_id"),
            "is_active": True
        }
    except ValueError:
        raise UnauthorizedException(detail="Could not validate credentials")

def get_current_active_user(
    current_user: Annotated[dict[str, Any], Depends(get_current_user)]
) -> dict[str, Any]:
    """Check if the current user is active."""
    if not current_user.get("is_active"):
        raise ForbiddenException(detail="Inactive user")
    return current_user

def require_role(*roles: str):
    """Return a dependency that checks if the user has one of the required roles (owner automatically inherits staff permissions)."""
    allowed_roles = set(roles)
    if "staff" in allowed_roles:
        allowed_roles.add("owner")
        
    def role_checker(
        current_user: Annotated[dict[str, Any], Depends(get_current_active_user)]
    ) -> dict[str, Any]:
        if current_user.get("role") not in allowed_roles:
            raise ForbiddenException(detail="Operation not permitted")
        return current_user
    return role_checker


def get_business_context(
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)]
) -> str:
    """Extract business_id from current user for tenant scoping."""
    business_id = current_user.get("business_id")
    if not business_id:
        raise ForbiddenException(detail="No business context available")
    return business_id
