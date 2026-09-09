"""
User domain schemas for serialization and profile updates.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserRead(BaseModel):
    """Safe user representation returned in API responses."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserUpdate(BaseModel):
    """Payload for updating user profile information."""
    full_name: Optional[str] = Field(None, min_length=1, max_length=150)
    email: Optional[EmailStr] = None
