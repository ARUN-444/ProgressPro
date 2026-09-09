"""
Fitness profile API endpoints: anthropometrics, experience, and training goal management.
"""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.fitness_profile import (
    FitnessProfileCreate,
    FitnessProfileRead,
    FitnessProfileUpdate,
)
from app.services.profile_service import ProfileService

router = APIRouter(prefix="/profile", tags=["Fitness Profile"])


@router.get(
    "",
    response_model=FitnessProfileRead,
    summary="Get authenticated user's fitness profile",
)
@router.get(
    "/me",
    response_model=FitnessProfileRead,
    include_in_schema=False,
)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieves the fitness profile associated with the authenticated user."""
    service = ProfileService(db)
    return service.get_profile(current_user.id)


@router.post(
    "",
    response_model=FitnessProfileRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create fitness profile for authenticated user",
)
@router.post(
    "/me",
    response_model=FitnessProfileRead,
    status_code=status.HTTP_201_CREATED,
    include_in_schema=False,
)
def create_my_profile(
    profile_data: FitnessProfileCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Sets up the initial baseline fitness attributes (height, weight, goals, activity level)."""
    service = ProfileService(db)
    return service.create_profile(current_user.id, profile_data)


@router.put(
    "",
    response_model=FitnessProfileRead,
    summary="Update authenticated user's fitness profile",
)
@router.put(
    "/me",
    response_model=FitnessProfileRead,
    include_in_schema=False,
)
def update_my_profile(
    profile_data: FitnessProfileUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Updates attributes of the user's fitness profile."""
    service = ProfileService(db)
    return service.update_profile(current_user.id, profile_data)
