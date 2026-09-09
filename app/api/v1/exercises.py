"""
Exercise catalog and custom exercise API endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.exercise import ExerciseCreate, ExerciseRead
from app.services.exercise_service import ExerciseService

router = APIRouter(prefix="/exercises", tags=["Exercises"])


@router.get(
    "",
    response_model=List[ExerciseRead],
    summary="List and filter exercises",
)
def list_exercises(
    category: Optional[str] = Query(None, description="Filter by category (e.g. 'barbell', 'dumbbell')"),
    primary_muscle_group: Optional[str] = Query(None, description="Filter by muscle group (e.g. 'chest', 'back')"),
    search: Optional[str] = Query(None, description="Search exercise by name"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Returns available exercise catalog items (both public library and custom movements created by user)."""
    service = ExerciseService(db)
    return service.list_exercises(
        category=category,
        primary_muscle_group=primary_muscle_group,
        user_id=current_user.id,
        search=search,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=ExerciseRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a custom exercise",
)
def create_custom_exercise(
    data: ExerciseCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Creates a custom exercise associated with the authenticated user."""
    data.is_custom = True
    service = ExerciseService(db)
    return service.create_exercise(data, user_id=current_user.id)


@router.get(
    "/{exercise_id}",
    response_model=ExerciseRead,
    summary="Get exercise details by ID",
)
def get_exercise_details(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Fetch details for a specific exercise in the library."""
    service = ExerciseService(db)
    return service.get_exercise_by_id(exercise_id)


@router.delete(
    "/{exercise_id}",
    response_model=MessageResponse,
    summary="Delete a custom exercise",
)
def delete_exercise(
    exercise_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deletes a custom exercise created by the user."""
    service = ExerciseService(db)
    service.delete_custom_exercise(exercise_id, user_id=current_user.id)
    return MessageResponse(message="Exercise successfully deleted")
