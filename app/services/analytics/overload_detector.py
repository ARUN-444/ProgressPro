"""
Progressive overload detection module.
Evaluates weight, rep, and volume progressions across successive training sessions.
"""

from decimal import Decimal
from typing import List, Tuple
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException, InsufficientDataException
from app.models.workout import Workout, WorkoutExercise
from app.repositories.exercise_repo import ExerciseRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.analytics import ProgressiveOverloadResponse


class OverloadDetector:
    """
    Detects progressive overload along load, repetition, and volume dimensions.
    """

    def __init__(self, db: Session):
        self.db = db
        self.workout_repo = WorkoutRepository(db)
        self.exercise_repo = ExerciseRepository(db)

    def detect_overload(self, user_id: int, exercise_id: int) -> ProgressiveOverloadResponse:
        """
        Compares the two most recent workout sessions containing the target exercise.
        """
        exercise = self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise EntityNotFoundException(f"Exercise with ID {exercise_id} not found")

        # Fetch recent workouts for user
        workouts = self.workout_repo.list_by_user(user_id=user_id, limit=50)

        # Filter to workouts that include this exercise
        relevant_sessions: List[Tuple[Workout, WorkoutExercise]] = []
        for w in workouts:
            for we in w.workout_exercises:
                if we.exercise_id == exercise_id and we.exercise_sets:
                    relevant_sessions.append((w, we))
                    break

        if len(relevant_sessions) < 2:
            raise InsufficientDataException(
                f"At least 2 workouts with exercise '{exercise.name}' are required to evaluate progressive overload",
                details={"exercise_id": exercise_id, "workouts_found": len(relevant_sessions), "minimum_required": 2},
            )

        # relevant_sessions[0] is the most recent (session 2), relevant_sessions[1] is the preceding one (session 1)
        w_current, we_current = relevant_sessions[0]
        w_prev, we_prev = relevant_sessions[1]

        # Extract top set (highest weight * reps) and total volume for previous session
        prev_top_w = Decimal("0.00")
        prev_top_r = 0
        prev_volume = Decimal("0.00")
        for s in we_prev.exercise_sets:
            if not s.is_completed or s.set_type == "warmup":
                continue
            set_vol = Decimal(str(s.weight_kg)) * Decimal(str(s.reps))
            prev_volume += set_vol
            if s.weight_kg > prev_top_w or (s.weight_kg == prev_top_w and s.reps > prev_top_r):
                prev_top_w = s.weight_kg
                prev_top_r = s.reps

        # Extract top set and total volume for current session
        curr_top_w = Decimal("0.00")
        curr_top_r = 0
        curr_volume = Decimal("0.00")
        for s in we_current.exercise_sets:
            if not s.is_completed or s.set_type == "warmup":
                continue
            set_vol = Decimal(str(s.weight_kg)) * Decimal(str(s.reps))
            curr_volume += set_vol
            if s.weight_kg > curr_top_w or (s.weight_kg == curr_top_w and s.reps > curr_top_r):
                curr_top_w = s.weight_kg
                curr_top_r = s.reps

        delta_w = curr_top_w - prev_top_w
        delta_r = curr_top_r - prev_top_r
        delta_vol_pct = (
            ((curr_volume - prev_volume) / prev_volume * Decimal("100.0"))
            if prev_volume > Decimal("0.00")
            else Decimal("0.00")
        )

        # Classify overload
        if delta_w > Decimal("0.00") and curr_top_r >= prev_top_r:
            status = "OVERLOAD_ACHIEVED"
            dimension = "LOAD_INCREASE"
            explanation = f"Increased top-set load by +{delta_w}kg while maintaining/improving reps."
        elif curr_top_w >= prev_top_w and delta_r > 0:
            status = "OVERLOAD_ACHIEVED"
            dimension = "REP_INCREASE"
            explanation = f"Increased top-set repetitions by +{delta_r} reps at the same/higher load."
        elif delta_vol_pct >= Decimal("2.50"):
            status = "OVERLOAD_ACHIEVED"
            dimension = "VOLUME_INCREASE"
            explanation = f"Increased total exercise tonnage by +{delta_vol_pct.quantize(Decimal('0.1'))}%."
        elif delta_w < Decimal("-2.50") or delta_vol_pct < Decimal("-5.00"):
            status = "REGRESSION"
            dimension = "NONE"
            explanation = f"Performance declined compared to previous session (tonnage changed by {delta_vol_pct.quantize(Decimal('0.1'))}%)."
        else:
            status = "PLATEAU"
            dimension = "NONE"
            explanation = "Load and repetitions were essentially unchanged from the previous session."

        return ProgressiveOverloadResponse(
            exercise_id=exercise.id,
            exercise_name=exercise.name,
            status=status,
            overload_dimension=dimension,
            delta_load_kg=delta_w,
            delta_reps=delta_r,
            delta_volume_percentage=delta_vol_pct.quantize(Decimal("0.01")),
            explanation=explanation,
        )
