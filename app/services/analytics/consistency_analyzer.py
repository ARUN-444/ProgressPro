"""
Workout consistency and habit adherence module.
Computes training frequency, goal adherence percentage, and active weekly workout streaks.
"""

from collections import defaultdict
from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.analytics import ConsistencyResponse


class ConsistencyAnalyzer:
    """
    Evaluates consistency metrics over rolling time windows.
    """

    def __init__(self, db: Session):
        self.db = db
        self.workout_repo = WorkoutRepository(db)

    def analyze_consistency(
        self,
        user_id: int,
        evaluation_window_days: int = 30,
        target_frequency_per_week: int = 4,
    ) -> ConsistencyResponse:
        """
        Computes adherence and active weekly streaks for an athlete.
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=evaluation_window_days)

        workouts = self.workout_repo.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=200,
        )

        total_workouts = len(workouts)
        weeks_in_window = max(1.0, evaluation_window_days / 7.0)
        actual_frequency = round(total_workouts / weeks_in_window, 1)

        expected_workouts = target_frequency_per_week * weeks_in_window
        if expected_workouts > 0:
            adherence_pct = min(100.0, round((total_workouts / expected_workouts) * 100.0, 1))
        else:
            adherence_pct = 0.0

        # Calculate active streak in consecutive ISO weeks
        # Fetch longer 12-week history to compute active streak
        streak_start = end_date - timedelta(days=84)
        all_recent_workouts = self.workout_repo.list_by_user(
            user_id=user_id,
            start_date=streak_start,
            end_date=end_date,
            limit=200,
        )

        workouts_per_iso_week = defaultdict(int)
        for w in all_recent_workouts:
            iso_year, iso_week, _ = w.workout_date.isocalendar()
            workouts_per_iso_week[(iso_year, iso_week)] += 1

        # Current ISO week
        cur_year, cur_week, _ = end_date.isocalendar()
        streak = 0
        min_threshold = max(2, target_frequency_per_week - 1)

        # Check current week and previous consecutive weeks
        check_date = end_date
        while True:
            y, w, _ = check_date.isocalendar()
            count = workouts_per_iso_week.get((y, w), 0)
            if count >= min_threshold:
                streak += 1
                check_date -= timedelta(days=7)
            else:
                break

        return ConsistencyResponse(
            evaluation_window_days=evaluation_window_days,
            target_frequency_per_week=target_frequency_per_week,
            actual_frequency_per_week=actual_frequency,
            adherence_percentage=adherence_pct,
            current_active_streak_weeks=streak,
            total_workouts_completed=total_workouts,
        )
