"""
Schemas for analytics data outputs:
Volume, strength trends, consistency, progressive overload, recovery, and progress scoring.
"""

from datetime import date
from decimal import Decimal
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Volume Analytics
# ---------------------------------------------------------------------------

class MuscleGroupVolume(BaseModel):
    """Volume load metrics for an individual muscle group."""
    muscle_group: str
    total_tonnage_kg: Decimal
    effective_working_sets: int
    volume_landmark_status: str = Field(
        description="'below_mev', 'mev_to_mav', 'mav_to_mrv', 'above_mrv'"
    )


class VolumeAnalyticsResponse(BaseModel):
    """Aggregated volume analysis for a training period."""
    start_date: date
    end_date: date
    total_sessions: int
    total_tonnage_kg: Decimal
    muscle_group_breakdown: List[MuscleGroupVolume]


# ---------------------------------------------------------------------------
# Strength Progression (1RM Estimation)
# ---------------------------------------------------------------------------

class StrengthHistoryPoint(BaseModel):
    """Individual historical session strength entry."""
    workout_date: date
    top_weight_kg: Decimal
    reps_completed: int
    estimated_1rm_kg: Decimal


class StrengthProgressionResponse(BaseModel):
    """1RM progression trend and slope for a specific exercise."""
    exercise_id: int
    exercise_name: str
    current_estimated_1rm_kg: Decimal
    baseline_estimated_1rm_kg: Decimal
    percentage_change: Decimal
    weekly_slope_kg: Decimal
    history: List[StrengthHistoryPoint]


# ---------------------------------------------------------------------------
# Workout Consistency & Streaks
# ---------------------------------------------------------------------------

class ConsistencyResponse(BaseModel):
    """Training adherence and cadence metrics."""
    evaluation_window_days: int
    target_frequency_per_week: int
    actual_frequency_per_week: float
    adherence_percentage: float
    current_active_streak_weeks: int
    total_workouts_completed: int


# ---------------------------------------------------------------------------
# Progressive Overload Detection
# ---------------------------------------------------------------------------

class ProgressiveOverloadResponse(BaseModel):
    """Overload classification between successive training sessions of an exercise."""
    exercise_id: int
    exercise_name: str
    status: str = Field(description="'OVERLOAD_ACHIEVED', 'PLATEAU', 'REGRESSION'")
    overload_dimension: Optional[str] = Field(
        None, description="'LOAD_INCREASE', 'REP_INCREASE', 'VOLUME_INCREASE', 'NONE'"
    )
    delta_load_kg: Decimal
    delta_reps: int
    delta_volume_percentage: Decimal
    explanation: str


# ---------------------------------------------------------------------------
# Recovery & Sleep Debt
# ---------------------------------------------------------------------------

class RecoveryResponse(BaseModel):
    """Fatigue accumulation and sleep recovery index."""
    evaluation_window_days: int
    rolling_average_sleep_hours: Decimal
    accumulated_sleep_debt_hours: Decimal
    average_quality_score: Decimal
    recovery_score: int = Field(ge=0, le=100, description="Normalized score from 0 to 100")
    recovery_status: str = Field(description="'OPTIMAL', 'ADEQUATE', 'COMPROMISED'")


# ---------------------------------------------------------------------------
# Composite Overall Progress Scoring
# ---------------------------------------------------------------------------

class PillarBreakdown(BaseModel):
    """Component scores contributing to the overall progress score."""
    consistency_score: float = Field(ge=0.0, le=100.0)
    overload_score: float = Field(ge=0.0, le=100.0)
    volume_adherence_score: float = Field(ge=0.0, le=100.0)
    recovery_score: float = Field(ge=0.0, le=100.0)
    nutrition_adherence_score: float = Field(ge=0.0, le=100.0)


class OverallProgressScoreResponse(BaseModel):
    """Comprehensive multi-factor progress score."""
    score: int = Field(ge=0, le=100)
    rating: str = Field(description="'EXCELLENT', 'GOOD', 'FAIR', 'NEEDS_ATTENTION'")
    pillars: PillarBreakdown
    summary: str
