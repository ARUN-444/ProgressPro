"""
Security and authentication utilities for ProgressPro.
Provides password hashing via bcrypt and JWT token generation/verification via PyJWT.
"""

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional
import bcrypt
import jwt
from fastapi.security import OAuth2PasswordBearer
from app.core.config import settings
from app.core.exceptions import AuthenticationFailedException

# OAuth2 token scheme - used in future phases for protected endpoints
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login",
    auto_error=False,
)


def hash_password(password: str) -> str:
    """
    Hashes a plain-text password using bcrypt with a salt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that a plain-text password matches a stored bcrypt hash.
    """
    try:
        return bcrypt.checkpw(
            plain_password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )
    except Exception:
        return False


def create_access_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
    extra_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """
    Generates a signed JWT access token.
    Default expiry is configured via settings.ACCESS_TOKEN_EXPIRE_MINUTES.
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: str | int,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generates a signed JWT refresh token for long-lived sessions.
    Default expiry is configured via settings.REFRESH_TOKEN_EXPIRE_DAYS.
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS))

    payload: Dict[str, Any] = {
        "sub": str(subject),
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
        "type": "refresh",
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token(token: str) -> Dict[str, Any]:
    """
    Decodes and validates a JWT token signature and expiration.
    Raises AuthenticationFailedException if invalid or expired.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailedException("Token has expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailedException("Invalid token signature or format")
