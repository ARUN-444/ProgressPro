"""
Nutrition and macronutrient tracking schemas.
"""

from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class NutritionRecordCreate(BaseModel):
    """Payload to log a daily nutrition and macronutrient entry."""
    recorded_date: date = Field(description="Calendar date of the nutrition log")
    calories: int = Field(ge=0, le=15000, description="Total caloric intake in kcal")
    protein: Decimal = Field(ge=0.0, description="Total protein consumed in grams")
    carbs: Decimal = Field(ge=0.0, description="Total carbohydrates consumed in grams")
    fats: Decimal = Field(ge=0.0, description="Total fats consumed in grams")
    water: Optional[Decimal] = Field(None, ge=0.0, le=25.0, description="Total water intake in liters")


class NutritionRecordUpdate(BaseModel):
    """Payload to update an existing daily nutrition log."""
    calories: Optional[int] = Field(None, ge=0, le=15000)
    protein: Optional[Decimal] = Field(None, ge=0.0)
    carbs: Optional[Decimal] = Field(None, ge=0.0)
    fats: Optional[Decimal] = Field(None, ge=0.0)
    water: Optional[Decimal] = Field(None, ge=0.0, le=25.0)


class NutritionRecordRead(BaseModel):
    """Response schema representing a saved daily nutrition entry."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    recorded_date: date
    calories: int
    protein: Decimal
    carbs: Decimal
    fats: Decimal
    water: Optional[Decimal]
