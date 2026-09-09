"""
FitnessProfile request and response schemas.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class FitnessProfileCreate(BaseModel):
    """Payload to create an athlete's fitness profile."""
    gender: str = Field(description="Gender (e.g., 'male', 'female', 'other')")
    date_of_birth: date = Field(description="Date of birth")
    height_cm: Decimal = Field(ge=50.0, le=300.0, description="Height in centimeters")
    experience_level: str = Field(description="Experience level: 'beginner', 'intermediate', 'advanced'")
    primary_goal: str = Field(
        description="Goal: 'hypertrophy', 'strength', 'fat_loss', 'endurance', 'general_fitness'"
    )
    target_weight_kg: Optional[Decimal] = Field(None, ge=20.0, le=500.0, description="Target body weight in kg")
    activity_level: str = Field(
        description="Activity level: 'sedentary', 'lightly_active', 'moderately_active', 'very_active', 'extra_active'"
    )


class FitnessProfileUpdate(BaseModel):
    """Payload to update an athlete's fitness profile."""
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    height_cm: Optional[Decimal] = Field(None, ge=50.0, le=300.0)
    experience_level: Optional[str] = None
    primary_goal: Optional[str] = None
    target_weight_kg: Optional[Decimal] = Field(None, ge=20.0, le=500.0)
    activity_level: Optional[str] = None


class FitnessProfileRead(BaseModel):
    """Response schema representing a saved fitness profile."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    gender: str
    date_of_birth: date
    height_cm: Decimal
    experience_level: str
    primary_goal: str
    target_weight_kg: Optional[Decimal]
    activity_level: str
