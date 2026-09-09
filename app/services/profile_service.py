"""
Fitness profile service handling demographic and baseline fitness attributes.
"""

from sqlalchemy.orm import Session
from app.core.exceptions import DuplicateEntityException, EntityNotFoundException
from app.models.fitness_profile import FitnessProfile
from app.repositories.profile_repo import ProfileRepository
from app.schemas.fitness_profile import FitnessProfileCreate, FitnessProfileUpdate


class ProfileService:
    """Business logic for managing athlete fitness profiles."""

    def __init__(self, db: Session):
        self.db = db
        self.profile_repo = ProfileRepository(db)

    def get_profile(self, user_id: int) -> FitnessProfile:
        """Fetch the fitness profile for a user or raise EntityNotFoundException."""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            raise EntityNotFoundException("Fitness profile has not been created yet for this user")
        return profile

    def create_profile(self, user_id: int, data: FitnessProfileCreate) -> FitnessProfile:
        """Create a new fitness profile for an athlete (enforcing 1-to-1 relationship)."""
        existing = self.profile_repo.get_by_user_id(user_id)
        if existing:
            raise DuplicateEntityException("Fitness profile already exists for this user. Use PUT to update.")

        profile = FitnessProfile(
            user_id=user_id,
            gender=data.gender.lower(),
            date_of_birth=data.date_of_birth,
            height_cm=data.height_cm,
            experience_level=data.experience_level.lower(),
            primary_goal=data.primary_goal.lower(),
            target_weight_kg=data.target_weight_kg,
            activity_level=data.activity_level.lower(),
        )
        return self.profile_repo.create(profile)

    def update_profile(self, user_id: int, data: FitnessProfileUpdate) -> FitnessProfile:
        """Update an existing fitness profile."""
        profile = self.get_profile(user_id)

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None and isinstance(value, str):
                setattr(profile, key, value.lower())
            elif value is not None:
                setattr(profile, key, value)

        return self.profile_repo.update(profile)
