"""
Daily body weight tracking API endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.weight import WeightRecordCreate, WeightRecordRead, WeightRecordUpdate
from app.services.tracking_service import TrackingService

router = APIRouter(prefix="/tracking/weight", tags=["Weight Tracking"])


@router.post(
    "",
    response_model=WeightRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily body weight",
)
def log_weight(
    data: WeightRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Logs body weight and optional body fat percentage for a specific date."""
    service = TrackingService(db)
    return service.log_weight(current_user.id, data)


@router.get(
    "",
    response_model=List[WeightRecordRead],
    summary="Get body weight history",
)
def get_weight_history(
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieves chronologically sorted daily weight logs."""
    service = TrackingService(db)
    return service.get_weight_history(current_user.id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)


@router.put(
    "/{record_id}",
    response_model=WeightRecordRead,
    summary="Update a weight log entry",
)
def update_weight(
    record_id: int,
    data: WeightRecordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Updates an existing weight record."""
    service = TrackingService(db)
    return service.update_weight(record_id, current_user.id, data)


@router.delete(
    "/{record_id}",
    response_model=MessageResponse,
    summary="Delete a weight log entry",
)
def delete_weight(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deletes an existing weight record."""
    service = TrackingService(db)
    service.delete_weight(record_id, current_user.id)
    return MessageResponse(message="Weight record successfully deleted")
