"""
Authentication API endpoints: registration, login, and token refresh.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.schemas.auth import RefreshTokenRequest, TokenResponse, UserLogin, UserRegister
from app.schemas.user import UserRead
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
def register(
    reg_data: UserRegister,
    db: Session = Depends(get_db),
):
    """Creates a new user profile with a hashed password."""
    service = AuthService(db)
    return service.register_user(reg_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain access and refresh tokens",
)
def login(
    login_data: UserLogin,
    db: Session = Depends(get_db),
):
    """Authenticates credentials and returns signed JWT tokens."""
    service = AuthService(db)
    return service.authenticate_user(login_data)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh an expired access token",
)
def refresh(
    refresh_data: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Exchanges a valid refresh token for a fresh access token."""
    service = AuthService(db)
    return service.refresh_access_token(refresh_data.refresh_token)
