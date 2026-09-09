"""
Workout repository handling complex nested workout logging and time-series queries.
Uses SQLAlchemy 2.0 selectinload to eliminate N+1 queries.
"""

from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from app.models.workout import Workout, WorkoutExercise
from app.repositories.base import BaseRepository


class WorkoutRepository(BaseRepository[Workout]):
    """
    Data access layer for Workout sessions and nested exercises/sets.
    """

    def __init__(self, db: Session):
        super().__init__(Workout, db)

    def get_by_id(self, workout_id: int, user_id: Optional[int] = None) -> Optional[Workout]:
        """
        Fetch a workout session with all nested workout exercises and sets eager-loaded.
        Optionally validates ownership if user_id is provided.
        """
        stmt = (
            select(Workout)
            .options(
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.exercise_sets),
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.exercise),
            )
            .where(Workout.id == workout_id)
        )

        if user_id is not None:
            stmt = stmt.where(Workout.user_id == user_id)

        return self.db.scalars(stmt).first()

    def list_by_user(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Workout]:
        """
        List workout sessions for a user within an optional date range,
        with complete nested sets eager loaded for analytics.
        """
        stmt = (
            select(Workout)
            .options(
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.exercise_sets),
                selectinload(Workout.workout_exercises)
                .selectinload(WorkoutExercise.exercise),
            )
            .where(Workout.user_id == user_id)
        )

        if start_date:
            stmt = stmt.where(Workout.workout_date >= start_date)
        if end_date:
            stmt = stmt.where(Workout.workout_date <= end_date)

        stmt = stmt.order_by(Workout.workout_date.desc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def count_by_user(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        """Count total workouts logged by a user within an optional date range."""
        from sqlalchemy import func
        stmt = select(func.count(Workout.id)).where(Workout.user_id == user_id)
        if start_date:
            stmt = stmt.where(Workout.workout_date >= start_date)
        if end_date:
            stmt = stmt.where(Workout.workout_date <= end_date)
        return self.db.scalar(stmt) or 0
