"""
Body weight and body fat tracking schemas.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class WeightRecordCreate(BaseModel):
    """Payload to log a daily body weight entry."""
    recorded_date: date = Field(description="Date of the weigh-in")
    weight_kg: Decimal = Field(ge=20.0, le=500.0, description="Measured weight in kilograms")
    body_fat_percentage: Optional[Decimal] = Field(
        None, ge=2.0, le=70.0, description="Optional measured body fat percentage"
    )
    notes: Optional[str] = Field(None, max_length=255, description="Weigh-in conditions (e.g. fasted)")


class WeightRecordUpdate(BaseModel):
    """Payload to update an existing weight entry."""
    weight_kg: Optional[Decimal] = Field(None, ge=20.0, le=500.0)
    body_fat_percentage: Optional[Decimal] = Field(None, ge=2.0, le=70.0)
    notes: Optional[str] = Field(None, max_length=255)


class WeightRecordRead(BaseModel):
    """Response schema representing a saved weight record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recorded_date: date
    weight_kg: Decimal
    body_fat_percentage: Optional[Decimal]
    notes: Optional[str]
