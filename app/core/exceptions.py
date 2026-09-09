"""
Custom domain exceptions and error handling structures for ProgressPro.
Provides clean, consistent error responses across all API endpoints.
"""

from typing import Any, Dict, Optional
from fastapi import Request
from fastapi.responses import JSONResponse


class ProgressProException(Exception):
    """Base exception for all ProgressPro application errors."""

    def __init__(
        self,
        message: str,
        code: str = "APPLICATION_ERROR",
        status_code: int = 400,
        details: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details or {}


class EntityNotFoundException(ProgressProException):
    """Raised when a requested resource (user, workout, exercise, record) cannot be found."""

    def __init__(self, message: str = "Resource not found", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="NOT_FOUND",
            status_code=404,
            details=details,
        )


class DuplicateEntityException(ProgressProException):
    """Raised when attempting to create a duplicate record (e.g. duplicate email or daily log)."""

    def __init__(self, message: str = "Resource already exists", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="CONFLICT",
            status_code=409,
            details=details,
        )


class AuthenticationFailedException(ProgressProException):
    """Raised when authentication credentials are missing, invalid, or expired."""

    def __init__(self, message: str = "Authentication failed", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="UNAUTHORIZED",
            status_code=401,
            details=details,
        )


class PermissionDeniedException(ProgressProException):
    """Raised when an authenticated user attempts to access or mutate resources they do not own."""

    def __init__(self, message: str = "Permission denied", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="FORBIDDEN",
            status_code=403,
            details=details,
        )


class InsufficientDataException(ProgressProException):
    """Raised when progress analysis or overload detection requires more historical data points."""

    def __init__(self, message: str = "Insufficient data for analysis", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INSUFFICIENT_DATA",
            status_code=422,
            details=details,
        )


class InvalidMetricException(ProgressProException):
    """Raised when input fitness or nutrition metrics violate domain ranges."""

    def __init__(self, message: str = "Invalid metric value", details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            code="INVALID_METRIC",
            status_code=400,
            details=details,
        )


async def progresspro_exception_handler(request: Request, exc: ProgressProException) -> JSONResponse:
    """
    FastAPI global exception handler for ProgressProException and its subclasses.
    Formats errors into a standard JSON envelope.
    """
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            },
        },
    )
