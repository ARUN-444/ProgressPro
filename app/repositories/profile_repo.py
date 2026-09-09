"""
FitnessProfile repository handling demographic and fitness profile records.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.fitness_profile import FitnessProfile
from app.repositories.base import BaseRepository


class ProfileRepository(BaseRepository[FitnessProfile]):
    """
    Data access layer for FitnessProfile entities.
    """

    def __init__(self, db: Session):
        super().__init__(FitnessProfile, db)

    def get_by_user_id(self, user_id: int) -> Optional[FitnessProfile]:
        """Fetch the unique fitness profile belonging to a user."""
        stmt = select(FitnessProfile).where(FitnessProfile.user_id == user_id)
        return self.db.scalars(stmt).first()
