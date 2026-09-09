"""
Authentication service handling user registration, password verification, and token issuance.
"""

from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationFailedException, DuplicateEntityException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.auth import TokenResponse, UserLogin, UserRegister


class AuthService:
    """Business logic for authentication workflows."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def register_user(self, reg_data: UserRegister) -> User:
        """Register a new user account with hashed credentials."""
        existing = self.user_repo.get_by_email(reg_data.email)
        if existing:
            raise DuplicateEntityException(f"Email '{reg_data.email}' is already registered")

        hashed = hash_password(reg_data.password)
        new_user = User(
            email=reg_data.email,
            hashed_password=hashed,
            full_name=reg_data.full_name,
            is_active=True,
        )
        return self.user_repo.create(new_user)

    def authenticate_user(self, login_data: UserLogin) -> TokenResponse:
        """Authenticate user credentials and return access/refresh tokens."""
        user = self.user_repo.get_by_email(login_data.email)
        if not user or not verify_password(login_data.password, user.hashed_password):
            raise AuthenticationFailedException("Incorrect email or password")

        if not user.is_active:
            raise AuthenticationFailedException("User account is disabled")

        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )

    def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """Issue a new access token from a valid refresh token."""
        payload = decode_token(refresh_token)
        if payload.get("type") != "refresh":
            raise AuthenticationFailedException("Invalid token type: refresh token expected")

        sub = payload.get("sub")
        if not sub:
            raise AuthenticationFailedException("Invalid token subject")

        user = self.user_repo.get_by_id(int(sub))
        if not user or not user.is_active:
            raise AuthenticationFailedException("User account no longer active")

        new_access_token = create_access_token(user.id)
        return TokenResponse(
            access_token=new_access_token,
            refresh_token=refresh_token,
            token_type="bearer",
        )
