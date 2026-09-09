"""
Mathematical Analytics API endpoints:
Volume analysis, 1RM strength trends, workout consistency, progressive overload, recovery, and overall score.
"""

from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.analytics import (
    ConsistencyResponse,
    OverallProgressScoreResponse,
    ProgressiveOverloadResponse,
    RecoveryResponse,
    StrengthProgressionResponse,
    VolumeAnalyticsResponse,
)
from app.services.analytics.consistency_analyzer import ConsistencyAnalyzer
from app.services.analytics.overload_detector import OverloadDetector
from app.services.analytics.progress_scorer import ProgressScorer
from app.services.analytics.recovery_analyzer import RecoveryAnalyzer
from app.services.analytics.strength_analyzer import StrengthAnalyzer
from app.services.analytics.volume_analyzer import VolumeAnalyzer

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get(
    "/volume",
    response_model=VolumeAnalyticsResponse,
    summary="Analyze workout volume load and muscle landmarks",
)
def get_volume_analytics(
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Calculates total tonnage and classifies weekly working sets per muscle group against MEV/MAV/MRV landmarks."""
    analyzer = VolumeAnalyzer(db)
    return analyzer.analyze_volume(current_user.id, start_date=start_date, end_date=end_date)


@router.get(
    "/strength",
    response_model=StrengthProgressionResponse,
    summary="Analyze 1RM strength progression for an exercise",
)
def get_strength_progression(
    exercise_id: int = Query(..., description="ID of the exercise to evaluate"),
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Estimates session 1RMs using the Epley equation and calculates overall percentage change and weekly slope."""
    analyzer = StrengthAnalyzer(db)
    return analyzer.analyze_strength_progression(
        current_user.id,
        exercise_id=exercise_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/strength/{exercise_id}",
    response_model=StrengthProgressionResponse,
    include_in_schema=False,
)
def get_strength_progression_by_path(
    exercise_id: int,
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    analyzer = StrengthAnalyzer(db)
    return analyzer.analyze_strength_progression(
        current_user.id,
        exercise_id=exercise_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.get(
    "/consistency",
    response_model=ConsistencyResponse,
    summary="Analyze workout frequency and active weekly streak",
)
def get_consistency_analytics(
    window_days: int = Query(30, ge=7, le=180, description="Evaluation window in days"),
    target_frequency: int = Query(4, ge=1, le=7, description="Target workouts per week"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Evaluates training consistency percentage and streaks over rolling days."""
    analyzer = ConsistencyAnalyzer(db)
    return analyzer.analyze_consistency(
        current_user.id,
        evaluation_window_days=window_days,
        target_frequency_per_week=target_frequency,
    )


@router.get(
    "/progressive-overload",
    response_model=ProgressiveOverloadResponse,
    summary="Detect progressive overload for an exercise",
)
def get_progressive_overload(
    exercise_id: int = Query(..., description="ID of the exercise to evaluate"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Compares the two most recent sessions to verify load, repetition, or volume progressive overload."""
    detector = OverloadDetector(db)
    return detector.detect_overload(current_user.id, exercise_id=exercise_id)


@router.get(
    "/progressive-overload/{exercise_id}",
    response_model=ProgressiveOverloadResponse,
    include_in_schema=False,
)
def get_progressive_overload_by_path(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    detector = OverloadDetector(db)
    return detector.detect_overload(current_user.id, exercise_id=exercise_id)


@router.get(
    "/recovery",
    response_model=RecoveryResponse,
    summary="Analyze sleep duration, sleep debt, and recovery score",
)
def get_recovery_analytics(
    window_days: int = Query(7, ge=3, le=30, description="Rolling window in days"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Computes accumulated sleep debt and a normalized 0-100 recovery readiness score."""
    analyzer = RecoveryAnalyzer(db)
    return analyzer.analyze_recovery(current_user.id, evaluation_window_days=window_days)


@router.get(
    "/progress-score",
    response_model=OverallProgressScoreResponse,
    summary="Get multi-pillar overall progress score (0-100)",
)
def get_overall_progress_score(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Returns a composite 0-100 score weighted across consistency, overload, volume, recovery, and nutrition."""
    scorer = ProgressScorer(db)
    return scorer.calculate_overall_score(current_user.id)
