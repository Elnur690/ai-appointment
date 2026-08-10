from typing import Annotated, Any
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.core.dependencies import get_current_active_user

router = APIRouter()

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class UserInfoResponse(BaseModel):
    id: str
    role: str
    business_id: str | None = None
    is_active: bool

@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Authenticate user and return JWT tokens."""
    # TODO: Implement user lookup, password verification, and token generation
    return TokenResponse(access_token="placeholder_token")

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    db: Annotated[AsyncSession, Depends(get_db)]
):
    """Refresh access token."""
    # TODO: Implement refresh token validation and new token generation
    return TokenResponse(access_token="placeholder_new_token")

@router.get("/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: Annotated[dict[str, Any], Depends(get_current_active_user)]
):
    """Get current user information."""
    return UserInfoResponse(
        id=current_user["id"],
        role=current_user["role"],
        business_id=current_user.get("business_id"),
        is_active=current_user.get("is_active", True)
    )
