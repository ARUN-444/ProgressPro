"""
Exercise repository handling standard catalog and custom movements.
"""

from typing import Optional, Sequence
from sqlalchemy import or_, select
from sqlalchemy.orm import Session
from app.models.exercise import Exercise
from app.repositories.base import BaseRepository


class ExerciseRepository(BaseRepository[Exercise]):
    """
    Data access layer for Exercise entities.
    """

    def __init__(self, db: Session):
        super().__init__(Exercise, db)

    def get_by_name(self, name: str) -> Optional[Exercise]:
        """Find an exercise by its unique name (case-insensitive search)."""
        stmt = select(Exercise).where(Exercise.name.ilike(name.strip()))
        return self.db.scalars(stmt).first()

    def list_exercises(
        self,
        category: Optional[str] = None,
        primary_muscle_group: Optional[str] = None,
        user_id: Optional[int] = None,
        search: Optional[str] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[Exercise]:
        """
        List exercises with optional filtering.
        If user_id is provided, includes system exercises plus the user's custom exercises.
        """
        stmt = select(Exercise)

        if user_id is not None:
            # Include public system exercises (is_custom=False) OR custom exercises created by this user
            stmt = stmt.where(
                or_(
                    Exercise.is_custom.is_(False),
                    Exercise.created_by_user_id == user_id,
                )
            )

        if category:
            stmt = stmt.where(Exercise.category == category.lower())

        if primary_muscle_group:
            stmt = stmt.where(Exercise.primary_muscle_group == primary_muscle_group.lower())

        if search:
            stmt = stmt.where(Exercise.name.ilike(f"%{search.strip()}%"))

        stmt = stmt.order_by(Exercise.name.asc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()
