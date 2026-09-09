"""
User service handling profile data queries and account updates.
"""

from sqlalchemy.orm import Session
from app.core.exceptions import DuplicateEntityException, EntityNotFoundException
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.schemas.user import UserUpdate


class UserService:
    """Business logic for user account management."""

    def __init__(self, db: Session):
        self.db = db
        self.user_repo = UserRepository(db)

    def get_user_by_id(self, user_id: int) -> User:
        """Fetch user by ID or raise EntityNotFoundException."""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            raise EntityNotFoundException(f"User with ID {user_id} not found")
        return user

    def update_user(self, user: User, update_data: UserUpdate) -> User:
        """Update user profile information."""
        if update_data.email and update_data.email != user.email:
            existing = self.user_repo.get_by_email(update_data.email)
            if existing:
                raise DuplicateEntityException(f"Email '{update_data.email}' is already registered")
            user.email = update_data.email

        if update_data.full_name is not None:
            user.full_name = update_data.full_name

        return self.user_repo.update(user)
