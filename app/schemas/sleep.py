"""
Sleep and daily recovery tracking schemas.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SleepRecordCreate(BaseModel):
    """Payload to log a daily sleep and recovery entry."""
    recorded_date: date = Field(description="Calendar date of the sleep log")
    sleep_duration_hours: Decimal = Field(
        ge=0.0, le=24.0, description="Total sleep duration in hours (e.g. 7.5)"
    )
    quality_score: int = Field(ge=1, le=5, description="Subjective sleep quality rating (1=poor to 5=excellent)")
    resting_heart_rate: Optional[int] = Field(
        None, ge=30, le=220, description="Optional morning resting heart rate in bpm"
    )
    notes: Optional[str] = Field(None, max_length=255, description="Sleep notes (e.g. woke up twice)")


class SleepRecordUpdate(BaseModel):
    """Payload to update an existing sleep entry."""
    sleep_duration_hours: Optional[Decimal] = Field(None, ge=0.0, le=24.0)
    quality_score: Optional[int] = Field(None, ge=1, le=5)
    resting_heart_rate: Optional[int] = Field(None, ge=30, le=220)
    notes: Optional[str] = Field(None, max_length=255)


class SleepRecordRead(BaseModel):
    """Response schema representing a saved sleep record."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recorded_date: date
    sleep_duration_hours: Decimal
    quality_score: int
    resting_heart_rate: Optional[int]
    notes: Optional[str]
