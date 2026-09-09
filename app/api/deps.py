"""
API dependencies for authentication, database session injection, and authorization.
"""

from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.exceptions import AuthenticationFailedException
from app.core.security import decode_token, oauth2_scheme
from app.models.user import User
from app.repositories.user_repo import UserRepository


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Decodes the Bearer JWT token, validates claims, and retrieves the authenticated User.
    Raises AuthenticationFailedException (HTTP 401) on missing or invalid credentials.
    """
    if not token:
        raise AuthenticationFailedException("Authentication token is required")

    payload = decode_token(token)
    sub = payload.get("sub")
    token_type = payload.get("type")

    if not sub or token_type != "access":
        raise AuthenticationFailedException("Invalid token type or missing subject claim")

    try:
        user_id = int(sub)
    except (ValueError, TypeError):
        raise AuthenticationFailedException("Malformed user identity in token")

    user_repo = UserRepository(db)
    user = user_repo.get_by_id(user_id)
    if not user:
        raise AuthenticationFailedException("User not found or account removed")

    return user


def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Ensures that the authenticated user's account is currently active.
    """
    if not current_user.is_active:
        raise AuthenticationFailedException("User account is disabled")
    return current_user
