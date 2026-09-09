"""
Workout logging and nested hierarchy schemas:
Workout -> WorkoutExercise -> ExerciseSet.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.exercise import ExerciseRead


# ---------------------------------------------------------------------------
# Exercise Set Schemas
# ---------------------------------------------------------------------------

class ExerciseSetCreate(BaseModel):
    """Payload to log a single set of an exercise."""
    set_number: int = Field(ge=1, description="Sequential index of the set (1-based)")
    set_type: str = Field(default="normal", description="'warmup', 'normal', 'drop_set', 'failure'")
    weight_kg: Decimal = Field(default=Decimal("0.00"), ge=0.0, description="Load in kilograms")
    reps: int = Field(default=0, ge=0, description="Number of completed repetitions")
    rpe: Optional[Decimal] = Field(None, ge=1.0, le=10.0, description="Rate of Perceived Exertion (1.0 to 10.0)")
    is_completed: bool = Field(default=True, description="True if the set was completed successfully")


class ExerciseSetRead(BaseModel):
    """Response schema representing a recorded exercise set."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_exercise_id: int
    set_number: int
    set_type: str
    weight_kg: Decimal
    reps: int
    rpe: Optional[Decimal]
    is_completed: bool


# ---------------------------------------------------------------------------
# Workout Exercise Schemas
# ---------------------------------------------------------------------------

class WorkoutExerciseCreate(BaseModel):
    """Payload to attach an exercise with its performed sets to a workout session."""
    exercise_id: int = Field(description="ID of the performed exercise")
    order: int = Field(default=1, ge=1, description="Order index of this exercise within the session")
    notes: Optional[str] = Field(None, max_length=255, description="Specific cues or performance notes")
    exercise_sets: List[ExerciseSetCreate] = Field(
        default_factory=list, description="List of sets completed for this exercise"
    )


class WorkoutExerciseRead(BaseModel):
    """Response schema representing an exercise performed during a workout."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    workout_id: int
    exercise_id: int
    order: int
    notes: Optional[str]
    exercise: Optional[ExerciseRead] = None
    exercise_sets: List[ExerciseSetRead] = []


# ---------------------------------------------------------------------------
# Workout Session Schemas
# ---------------------------------------------------------------------------

class WorkoutCreate(BaseModel):
    """Payload to log a complete workout session with nested exercises and sets."""
    title: str = Field(min_length=1, max_length=150, description="Session name (e.g. 'Push Hypertrophy')")
    workout_date: date = Field(description="Calendar date of the workout")
    start_time: Optional[datetime] = Field(None, description="Optional start timestamp")
    end_time: Optional[datetime] = Field(None, description="Optional end timestamp")
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440, description="Total session duration in minutes")
    rpe: Optional[Decimal] = Field(None, ge=1.0, le=10.0, description="Overall session perceived exertion (1-10)")
    notes: Optional[str] = Field(None, description="General session reflections or notes")
    workout_exercises: List[WorkoutExerciseCreate] = Field(
        default_factory=list, description="Ordered list of exercises performed"
    )


class WorkoutUpdate(BaseModel):
    """Payload to update an existing workout's top-level metadata."""
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    workout_date: Optional[date] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=1440)
    rpe: Optional[Decimal] = Field(None, ge=1.0, le=10.0)
    notes: Optional[str] = None


class WorkoutRead(BaseModel):
    """Fully nested response schema representing a completed workout session."""
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    workout_date: date
    start_time: Optional[datetime]
    end_time: Optional[datetime]
    duration_minutes: Optional[int]
    rpe: Optional[Decimal]
    notes: Optional[str]
    workout_exercises: List[WorkoutExerciseRead] = []
