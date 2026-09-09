"""
Daily nutrition and macronutrient tracking API endpoints.
"""

from datetime import date
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, get_db
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.nutrition import NutritionRecordCreate, NutritionRecordRead, NutritionRecordUpdate
from app.services.tracking_service import TrackingService

router = APIRouter(prefix="/tracking/nutrition", tags=["Nutrition Tracking"])


@router.post(
    "",
    response_model=NutritionRecordRead,
    status_code=status.HTTP_201_CREATED,
    summary="Log daily nutrition intake",
)
def log_nutrition(
    data: NutritionRecordCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Logs calories, protein, carbohydrates, fats, and water consumption for a date."""
    service = TrackingService(db)
    return service.log_nutrition(current_user.id, data)


@router.get(
    "",
    response_model=List[NutritionRecordRead],
    summary="Get nutrition history",
)
def get_nutrition_history(
    start_date: Optional[date] = Query(None, description="Start date (inclusive)"),
    end_date: Optional[date] = Query(None, description="End date (inclusive)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Retrieves chronologically sorted daily nutrition records."""
    service = TrackingService(db)
    return service.get_nutrition_history(current_user.id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)


@router.put(
    "/{record_id}",
    response_model=NutritionRecordRead,
    summary="Update a nutrition log entry",
)
def update_nutrition(
    record_id: int,
    data: NutritionRecordUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Updates an existing nutrition record."""
    service = TrackingService(db)
    return service.update_nutrition(record_id, current_user.id, data)


@router.delete(
    "/{record_id}",
    response_model=MessageResponse,
    summary="Delete a nutrition log entry",
)
def delete_nutrition(
    record_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    """Deletes an existing nutrition record."""
    service = TrackingService(db)
    service.delete_nutrition(record_id, current_user.id)
    return MessageResponse(message="Nutrition record successfully deleted")
