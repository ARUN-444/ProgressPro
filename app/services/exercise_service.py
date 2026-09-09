"""
Exercise service handling exercise catalog lookups and custom exercise creation.
"""

from typing import Optional, Sequence
from sqlalchemy.orm import Session
from app.core.exceptions import DuplicateEntityException, EntityNotFoundException, PermissionDeniedException
from app.models.exercise import Exercise
from app.repositories.exercise_repo import ExerciseRepository
from app.schemas.exercise import ExerciseCreate


class ExerciseService:
    """Business logic for exercise library and custom movements."""

    def __init__(self, db: Session):
        self.db = db
        self.exercise_repo = ExerciseRepository(db)

    def get_exercise_by_id(self, exercise_id: int) -> Exercise:
        """Fetch exercise by ID or raise EntityNotFoundException."""
        exercise = self.exercise_repo.get_by_id(exercise_id)
        if not exercise:
            raise EntityNotFoundException(f"Exercise with ID {exercise_id} not found")
        return exercise

    def list_exercises(
        self,
        category: Optional[str] = None,
        primary_muscle_group: Optional[str] = None,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Exercise]:
        """Fetch exercises matching query parameters."""
        return self.exercise_repo.list_exercises(
            category=category,
            primary_muscle_group=primary_muscle_group,
            user_id=user_id,
            search=search,
            skip=skip,
            limit=limit,
        )

    def create_exercise(self, data: ExerciseCreate, user_id: Optional[int] = None) -> Exercise:
        """Create a new standard or custom exercise."""
        existing = self.exercise_repo.get_by_name(data.name)
        if existing:
            raise DuplicateEntityException(f"Exercise '{data.name}' already exists in the catalog")

        exercise = Exercise(
            name=data.name.strip(),
            category=data.category.lower(),
            primary_muscle_group=data.primary_muscle_group.lower(),
            secondary_muscle_group=data.secondary_muscle_group.lower() if data.secondary_muscle_group else None,
            mechanics=data.mechanics.lower(),
            is_custom=data.is_custom,
            created_by_user_id=user_id if data.is_custom else None,
        )
        return self.exercise_repo.create(exercise)

    def delete_custom_exercise(self, exercise_id: int, user_id: int) -> None:
        """Delete a custom exercise owned by the user."""
        exercise = self.get_exercise_by_id(exercise_id)
        if not exercise.is_custom:
            raise PermissionDeniedException("Standard system exercises cannot be deleted")

        if exercise.created_by_user_id != user_id:
            raise PermissionDeniedException("You do not have permission to delete this exercise")

        self.exercise_repo.delete(exercise)
