"""
Common reusable schemas and response wrappers.
"""

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class MessageResponse(BaseModel):
    """Simple standard API message response."""
    message: str
    detail: Optional[str] = None


class PaginationParams(BaseModel):
    """Pagination query parameters."""
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=20, ge=1, le=100, description="Maximum records to return")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic envelope for paginated lists."""
    items: List[T]
    total: int
    skip: int
    limit: int
