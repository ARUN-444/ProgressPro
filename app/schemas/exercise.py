"""
Exercise library and custom exercise schemas.
"""

from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ExerciseCreate(BaseModel):
    """Payload to create a new standard or custom exercise."""
    name: str = Field(min_length=1, max_length=150, description="Unique name of the exercise")
    category: str = Field(description="Category: 'barbell', 'dumbbell', 'cable', 'machine', 'bodyweight', 'cardio'")
    primary_muscle_group: str = Field(
        description="Primary muscle group targeted (e.g., 'chest', 'back', 'quadriceps')"
    )
    secondary_muscle_group: Optional[str] = Field(
        None, max_length=100, description="Optional secondary muscle group assisted"
    )
    mechanics: str = Field(description="Movement mechanics: 'compound' or 'isolation'")
    is_custom: bool = Field(default=False, description="True if created by a specific user")


class ExerciseRead(BaseModel):
    """Response schema representing an exercise."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    category: str
    primary_muscle_group: str
    secondary_muscle_group: Optional[str]
    mechanics: str
    is_custom: bool
    created_by_user_id: Optional[int]


class ExerciseFilterParams(BaseModel):
    """Query filters for searching and categorizing exercises."""
    category: Optional[str] = None
    primary_muscle_group: Optional[str] = None
    is_custom: Optional[bool] = None
    search: Optional[str] = None
