"""
Authentication request and response schemas.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRegister(BaseModel):
    """Payload for new user account registration."""
    email: EmailStr = Field(description="Unique email address for the account")
    password: str = Field(min_length=6, max_length=128, description="User password (minimum 6 characters)")
    full_name: str = Field(min_length=1, max_length=150, description="Full name of the user")


class UserLogin(BaseModel):
    """Payload for user login credentials."""
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    """JWT token response containing access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    """Decoded JWT claims payload."""
    sub: str
    type: Optional[str] = "access"
    exp: Optional[int] = None


class RefreshTokenRequest(BaseModel):
    """Request payload to exchange a refresh token for a new access token."""
    refresh_token: str
