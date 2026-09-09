"""
User management API endpoints: authenticated user profile retrieval and updates.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.user import UserRead, UserUpdate
from app.services.user_service import UserService

router = APIRouter(prefix="/users", tags=["Users"])


@router.get(
    "/me",
    response_model=UserRead,
    summary="Get current authenticated user profile",
)
def get_current_user_profile(
    current_user: User = Depends(get_current_active_user),
):
    """Returns the profile of the currently logged-in athlete."""
    return current_user


@router.put(
    "/me",
    response_model=UserRead,
    summary="Update current authenticated user profile",
)
def update_current_user_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Updates user information (name, email) for the authenticated user."""
    service = UserService(db)
    return service.update_user(current_user, update_data)
