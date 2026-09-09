"""
Workout service orchestrating nested workout logging and session querying.
"""

from datetime import date
from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.core.exceptions import EntityNotFoundException, PermissionDeniedException
from app.models.workout import ExerciseSet, Workout, WorkoutExercise
from app.repositories.exercise_repo import ExerciseRepository
from app.repositories.workout_repo import WorkoutRepository
from app.schemas.workout import WorkoutCreate, WorkoutUpdate


class WorkoutService:
    """Business logic for workout tracking and session lifecycle."""

    def __init__(self, db: Session):
        self.db = db
        self.workout_repo = WorkoutRepository(db)
        self.exercise_repo = ExerciseRepository(db)

    def create_workout(self, user_id: int, data: WorkoutCreate) -> Workout:
        """
        Creates a complete workout session with nested exercises and sets in a single transaction.
        """
        # Validate that all referenced exercises exist
        for we_data in data.workout_exercises:
            ex = self.exercise_repo.get_by_id(we_data.exercise_id)
            if not ex:
                raise EntityNotFoundException(f"Exercise with ID {we_data.exercise_id} not found")

        workout = Workout(
            user_id=user_id,
            title=data.title,
            workout_date=data.workout_date,
            start_time=data.start_time,
            end_time=data.end_time,
            duration_minutes=data.duration_minutes,
            rpe=data.rpe,
            notes=data.notes,
        )

        for we_data in data.workout_exercises:
            we = WorkoutExercise(
                exercise_id=we_data.exercise_id,
                order=we_data.order,
                notes=we_data.notes,
            )
            for set_data in we_data.exercise_sets:
                es = ExerciseSet(
                    set_number=set_data.set_number,
                    set_type=set_data.set_type,
                    weight_kg=set_data.weight_kg,
                    reps=set_data.reps,
                    rpe=set_data.rpe,
                    is_completed=set_data.is_completed,
                )
                we.exercise_sets.append(es)
            workout.workout_exercises.append(we)

        created_workout = self.workout_repo.create(workout)
        # Reload with selectinload to ensure fully initialized response
        return self.workout_repo.get_by_id(created_workout.id, user_id=user_id) or created_workout

    def get_workout_by_id(self, workout_id: int, user_id: int) -> Workout:
        """Fetch workout session belonging to the user."""
        workout = self.workout_repo.get_by_id(workout_id)
        if not workout:
            raise EntityNotFoundException(f"Workout with ID {workout_id} not found")
        if workout.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to view this workout")
        return workout

    def list_workouts(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50,
    ) -> Sequence[Workout]:
        """List historical workouts for an athlete."""
        return self.workout_repo.list_by_user(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=limit,
        )

    def update_workout(self, workout_id: int, user_id: int, data: WorkoutUpdate) -> Workout:
        """Update top-level workout session metadata."""
        workout = self.get_workout_by_id(workout_id, user_id)

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(workout, key, value)

        return self.workout_repo.update(workout)

    def delete_workout(self, workout_id: int, user_id: int) -> None:
        """Delete a workout session and cascade delete all nested exercises and sets."""
        workout = self.get_workout_by_id(workout_id, user_id)
        self.workout_repo.delete(workout)
