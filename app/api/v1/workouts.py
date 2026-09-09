"""
Workout session tracking API endpoints.
Supports complete nested logging: Workout -> WorkoutExercise -> ExerciseSet.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.workout import WorkoutCreate, WorkoutRead, WorkoutUpdate
from app.services.workout_service import WorkoutService

router = APIRouter(prefix="/workouts", tags=["Workouts"])


@router.post(
    "",
    response_model=WorkoutRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log a completed workout session",
)
def log_workout(
    data: WorkoutCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Logs a completed session with all nested exercises, sets, weights, reps, and RPEs."""
    service = WorkoutService(db)
    return service.create_workout(current_user.id, data)


@router.get(
    "",
    response_model=List[WorkoutRead],
    summary="List workout history",
)
def list_workouts(
    start_date: Optional[date] = Query(None, description="Filter workouts from this date (inclusive)"),
    end_date: Optional[date] = Query(None, description="Filter workouts up to this date (inclusive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieves workout history with full nested exercise sets for the authenticated user."""
    service = WorkoutService(db)
    return service.list_workouts(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{workout_id}",
    response_model=WorkoutRead,
    summary="Get detailed workout session by ID",
)
def get_workout(
    workout_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Fetches a specific workout session with all nested sets and performance notes."""
    service = WorkoutService(db)
    return service.get_workout_by_id(workout_id, current_user.id)


@router.put(
    "/{workout_id}",
    response_model=WorkoutRead,
    summary="Update workout session metadata",
)
def update_workout(
    workout_id: int,
    data: WorkoutUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Updates session metadata (title, duration, RPE, notes)."""
    service = WorkoutService(db)
    return service.update_workout(workout_id, current_user.id, data)


@router.delete(
    "/{workout_id}",
    response_model=MessageResponse,
    summary="Delete a workout session",
)
def delete_workout(
    workout_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deletes a workout session and cascades deletion to all associated sets."""
    service = WorkoutService(db)
    service.delete_workout(workout_id, current_user.id)
    return MessageResponse(message="Workout session successfully deleted")
