"""
User repository handling database operations for user accounts.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """
    Data access layer for User entities.
    """

    def __init__(self, db: Session):
        super().__init__(User, db)

    def get_by_email(self, email: str) -> Optional[User]:
        """Fetch a user by their unique email address."""
        stmt = select(User).where(User.email == email)
        return self.db.scalars(stmt).first()
