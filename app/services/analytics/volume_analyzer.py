"""
Workout volume analysis module.
Calculates training volume load (tonnage), effective sets, and volume landmark classifications.
"""

from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal
from typing import Dict, List, Optional
from sqlalchemy.orm import Session

from app.models.workout import Workout
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.analytics import MuscleGroupVolume, VolumeAnalyticsResponse


class VolumeAnalyzer:
    """
    Computes volume metrics based on sports-science principles (Dr. Mike Israetel Volume Landmarks).
    """

    def __init__(self, db: Session):
        self.db = db
        self.workout_repo = WorkoutRepository(db)

    def analyze_volume(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> VolumeAnalyticsResponse:
        """
        Analyzes volume tonnage and set allocation across muscle groups for a date window.
        Defaults to the last 28 days (4 weeks) if dates are not specified.
        """
        today = date.today()
        end = end_date or today
        start = start_date or (end - timedelta(days=28))

        workouts = self.workout_repo.list_by_user(
            user_id=user_id,
            start_date=start,
            end_date=end,
            limit=200,
        )

        total_tonnage = Decimal("0.00")
        muscle_tonnage: Dict[str, Decimal] = defaultdict(Decimal)
        muscle_effective_sets: Dict[str, int] = defaultdict(int)

        for workout in workouts:
            for we in workout.workout_exercises:
                exercise = we.exercise
                muscle = exercise.primary_muscle_group.lower() if exercise else "other"

                for s in we.exercise_sets:
                    if not s.is_completed:
                        continue
                    # Warmup sets do not contribute to working tonnage or hypertrophy stimulus
                    if s.set_type == "warmup":
                        continue

                    set_tonnage = Decimal(str(s.weight_kg)) * Decimal(str(s.reps))
                    total_tonnage += set_tonnage
                    muscle_tonnage[muscle] += set_tonnage

                    # Effective working sets: normal, drop_set, failure
                    muscle_effective_sets[muscle] += 1

        # Calculate number of weeks in window (minimum 1 week to avoid division by zero)
        days = max(1, (end - start).days + 1)
        weeks = max(Decimal("1.0"), Decimal(str(days)) / Decimal("7.0"))

        muscle_breakdown: List[MuscleGroupVolume] = []
        all_muscles = set(muscle_tonnage.keys()) | set(muscle_effective_sets.keys())

        for muscle in sorted(all_muscles):
            sets_count = muscle_effective_sets[muscle]
            tonnage = muscle_tonnage[muscle]
            weekly_rate = Decimal(str(sets_count)) / weeks

            # Categorize using Dr. Mike Israetel volume landmarks:
            # MEV: ~10 sets/wk, MAV: 12-18 sets/wk, MRV: 20-22+ sets/wk
            if weekly_rate < Decimal("10.0"):
                status = "below_mev"
            elif Decimal("10.0") <= weekly_rate < Decimal("14.0"):
                status = "mev_to_mav"
            elif Decimal("14.0") <= weekly_rate <= Decimal("20.0"):
                status = "mav_to_mrv"
            else:
                status = "above_mrv"

            muscle_breakdown.append(
                MuscleGroupVolume(
                    muscle_group=muscle,
                    total_tonnage_kg=tonnage.quantize(Decimal("0.01")),
                    effective_working_sets=sets_count,
                    volume_landmark_status=status,
                )
            )

        return VolumeAnalyticsResponse(
            start_date=start,
            end_date=end,
            total_sessions=len(workouts),
            total_tonnage_kg=total_tonnage.quantize(Decimal("0.01")),
            muscle_group_breakdown=muscle_breakdown,
        )
