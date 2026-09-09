"""
Daily sleep and recovery tracking API endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.sleep import SleepRecordCreate, SleepRecordRead, SleepRecordUpdate
from app.services.tracking_service import TrackingService

router = APIRouter(prefix="/tracking/sleep", tags=["Sleep Tracking"])


@router.post(
    "",
    response_model=SleepRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily sleep duration and quality",
)
def log_sleep(
    data: SleepRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Logs hours of sleep, subjective quality (1-5), and resting heart rate."""
    service = TrackingService(db)
    return service.log_sleep(current_user.id, data)


@router.get(
    "",
    response_model=List[SleepRecordRead],
    summary="Get sleep history",
)
def get_sleep_history(
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieves chronologically sorted daily sleep records."""
    service = TrackingService(db)
    return service.get_sleep_history(current_user.id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)


@router.put(
    "/{record_id}",
    response_model=SleepRecordRead,
    summary="Update a sleep log entry",
)
def update_sleep(
    record_id: int,
    data: SleepRecordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Updates an existing sleep record."""
    service = TrackingService(db)
    return service.update_sleep(record_id, current_user.id, data)


@router.delete(
    "/{record_id}",
    response_model=MessageResponse,
    summary="Delete a sleep log entry",
)
def delete_sleep(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deletes an existing sleep record."""
    service = TrackingService(db)
    service.delete_sleep(record_id, current_user.id)
    return MessageResponse(message="Sleep record successfully deleted")
