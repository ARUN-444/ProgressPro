"""
Strength progression analysis module.
Computes estimated One-Repetition Maximum (1RM) progression and trend slopes using the Epley formula.
"""

from datetime import date
from decimal import Decimal
from typing import List, Optional
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException, InsufficientDataException
from app.models.workout import Workout
from app.repositories.exercise_repo import ExerciseRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.analytics import StrengthHistoryPoint, StrengthProgressionResponse


def calculate_epley_1rm(weight_kg: Decimal, reps: int) -> Decimal:
    """
    Computes estimated One-Repetition Maximum (1RM) via Epley's equation:
    1RM = weight * (1 + reps / 30.0)
    For 1 rep, 1RM equals the load lifted.
    """
    if reps <= 0 or weight_kg <= Decimal("0.00"):
        return Decimal("0.00")
    if reps == 1:
        return weight_kg
    # Epley formula
    e1rm = weight_kg * (Decimal("1.0") + (Decimal(str(reps)) / Decimal("30.0")))
    return e1rm.quantize(Decimal("0.01"))


class StrengthAnalyzer:
    """
    Analyzes strength trends across historical sessions for a given exercise.
    """

    def __init__(self, db: Session):
        self.db = db
        self.workout_repo = WorkoutRepository(db)
        self.exercise_repo = ExerciseRepository(db)

    def analyze_strength_progression(
        self,
        user_id: int,
        exercise_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> StrengthProgressionResponse:
        """
        Calculates session top-set e1RMs, net change percentage, and weekly progression slope.
        """
        exercise = self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise EntityNotFoundException(f"Exercise with ID {exercise_id} not found")

        workouts = self.workout_repo.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=200,
        )

        # Workouts are sorted desc from repo; reverse for chronological order
        chronological_workouts = list(reversed(workouts))
        history: List[StrengthHistoryPoint] = []

        for workout in chronological_workouts:
            top_e1rm = Decimal("0.00")
            top_weight = Decimal("0.00")
            top_reps = 0

            for we in workout.workout_exercises:
                if we.exercise_id != exercise_id:
                    continue

                for s in we.exercise_sets:
                    if not s.is_completed or s.set_type == "warmup":
                        continue

                    e1rm = calculate_epley_1rm(s.weight_kg, s.reps)
                    if e1rm > top_e1rm:
                        top_e1rm = e1rm
                        top_weight = s.weight_kg
                        top_reps = s.reps

            if top_e1rm > Decimal("0.00"):
                history.append(
                    StrengthHistoryPoint(
                        workout_date=workout.workout_date,
                        top_weight_kg=top_weight,
                        reps_completed=top_reps,
                        estimated_1rm_kg=top_e1rm,
                    )
                )

        if not history:
            raise InsufficientDataException(
                f"No completed workout sessions found containing exercise '{exercise.name}'",
                details={"exercise_id": exercise_id, "sessions_found": 0, "minimum_required": 1},
            )

        baseline_1rm = history[0].estimated_1rm_kg
        current_1rm = history[-1].estimated_1rm_kg

        if baseline_1rm > Decimal("0.00"):
            percent_change = ((current_1rm - baseline_1rm) / baseline_1rm) * Decimal("100.0")
        else:
            percent_change = Decimal("0.00")

        # Compute slope per week if multiple sessions exist
        if len(history) > 1:
            days_span = max(1, (history[-1].workout_date - history[0].workout_date).days)
            weeks_span = Decimal(str(days_span)) / Decimal("7.0")
            weeks_span = max(Decimal("0.5"), weeks_span)
            slope = (current_1rm - baseline_1rm) / weeks_span
        else:
            slope = Decimal("0.00")

        return StrengthProgressionResponse(
            exercise_id=exercise.id,
            exercise_name=exercise.name,
            current_estimated_1rm_kg=current_1rm,
            baseline_estimated_1rm_kg=baseline_1rm,
            percentage_change=percent_change.quantize(Decimal("0.01")),
            weekly_slope_kg=slope.quantize(Decimal("0.01")),
            history=history,
        )
