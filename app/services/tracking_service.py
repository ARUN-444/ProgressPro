"""
Tracking service handling daily health and recovery records:
Weight, Sleep, and Nutrition.
"""

from datetime import date
from typing import Optional, Sequence
from sqlalchemy.orm import Session

from app.core.exceptions import DuplicateEntityException, EntityNotFoundException, PermissionDeniedException
from app.models.nutrition_record import NutritionRecord
from app.models.sleep_record import SleepRecord
from app.models.weight_record import WeightRecord
from app.repositories.nutrition_repo import NutritionRepository
from app.repositories.sleep_repo import SleepRepository
from app.repositories.weight_repo import WeightRepository
from app.schemas.nutrition import NutritionRecordCreate, NutritionRecordUpdate
from app.schemas.sleep import SleepRecordCreate, SleepRecordUpdate
from app.schemas.weight import WeightRecordCreate, WeightRecordUpdate


class TrackingService:
    """Business logic for daily tracking entries with daily uniqueness constraints."""

    def __init__(self, db: Session):
        self.db = db
        self.weight_repo = WeightRepository(db)
        self.sleep_repo = SleepRepository(db)
        self.nutrition_repo = NutritionRepository(db)

    # -----------------------------------------------------------------------
    # Weight Tracking
    # -----------------------------------------------------------------------

    def log_weight(self, user_id: int, data: WeightRecordCreate) -> WeightRecord:
        """Log daily body weight, preventing duplicate entries for the same calendar date."""
        existing = self.weight_repo.get_by_user_and_date(user_id, data.recorded_date)
        if existing:
            raise DuplicateEntityException(
                f"Weight record already exists for date '{data.recorded_date}'. Update existing record."
            )
        record = WeightRecord(
            user_id=user_id,
            recorded_date=data.recorded_date,
            weight_kg=data.weight_kg,
            body_fat_percentage=data.body_fat_percentage,
            notes=data.notes,
        )
        return self.weight_repo.create(record)

    def get_weight_history(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[WeightRecord]:
        """Fetch historical weight entries for an athlete."""
        return self.weight_repo.list_by_user(user_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

    def update_weight(self, record_id: int, user_id: int, data: WeightRecordUpdate) -> WeightRecord:
        """Update an existing weight record."""
        record = self.weight_repo.get_by_id(record_id)
        if not record:
            raise EntityNotFoundException(f"Weight record with ID {record_id} not found")
        if record.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to modify this weight record")

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(record, key, value)
        return self.weight_repo.update(record)

    def delete_weight(self, record_id: int, user_id: int) -> None:
        """Delete a weight record."""
        record = self.weight_repo.get_by_id(record_id)
        if not record:
            raise EntityNotFoundException(f"Weight record with ID {record_id} not found")
        if record.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to delete this weight record")
        self.weight_repo.delete(record)

    # -----------------------------------------------------------------------
    # Sleep Tracking
    # -----------------------------------------------------------------------

    def log_sleep(self, user_id: int, data: SleepRecordCreate) -> SleepRecord:
        """Log daily sleep and recovery score."""
        existing = self.sleep_repo.get_by_user_and_date(user_id, data.recorded_date)
        if existing:
            raise DuplicateEntityException(
                f"Sleep record already exists for date '{data.recorded_date}'. Update existing record."
            )
        record = SleepRecord(
            user_id=user_id,
            recorded_date=data.recorded_date,
            sleep_duration_hours=data.sleep_duration_hours,
            quality_score=data.quality_score,
            resting_heart_rate=data.resting_heart_rate,
            notes=data.notes,
        )
        return self.sleep_repo.create(record)

    def get_sleep_history(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[SleepRecord]:
        """Fetch historical sleep logs for an athlete."""
        return self.sleep_repo.list_by_user(user_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

    def update_sleep(self, record_id: int, user_id: int, data: SleepRecordUpdate) -> SleepRecord:
        """Update an existing sleep record."""
        record = self.sleep_repo.get_by_id(record_id)
        if not record:
            raise EntityNotFoundException(f"Sleep record with ID {record_id} not found")
        if record.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to modify this sleep record")

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(record, key, value)
        return self.sleep_repo.update(record)

    def delete_sleep(self, record_id: int, user_id: int) -> None:
        """Delete a sleep record."""
        record = self.sleep_repo.get_by_id(record_id)
        if not record:
            raise EntityNotFoundException(f"Sleep record with ID {record_id} not found")
        if record.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to delete this sleep record")
        self.sleep_repo.delete(record)

    # -----------------------------------------------------------------------
    # Nutrition Tracking
    # -----------------------------------------------------------------------

    def log_nutrition(self, user_id: int, data: NutritionRecordCreate) -> NutritionRecord:
        """Log daily calories and macronutrient totals."""
        existing = self.nutrition_repo.get_by_user_and_date(user_id, data.recorded_date)
        if existing:
            raise DuplicateEntityException(
                f"Nutrition record already exists for date '{data.recorded_date}'. Update existing record."
            )
        record = NutritionRecord(
            user_id=user_id,
            recorded_date=data.recorded_date,
            calories=data.calories,
            protein=data.protein,
            carbs=data.carbs,
            fats=data.fats,
            water=data.water,
        )
        return self.nutrition_repo.create(record)

    def get_nutrition_history(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[NutritionRecord]:
        """Fetch historical daily nutrition logs for an athlete."""
        return self.nutrition_repo.list_by_user(user_id, start_date=start_date, end_date=end_date, skip=skip, limit=limit)

    def update_nutrition(self, record_id: int, user_id: int, data: NutritionRecordUpdate) -> NutritionRecord:
        """Update an existing nutrition record."""
        record = self.nutrition_repo.get_by_id(record_id)
        if not record:
            raise EntityNotFoundException(f"Nutrition record with ID {record_id} not found")
        if record.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to modify this nutrition record")

        update_fields = data.model_dump(exclude_unset=True)
        for key, value in update_fields.items():
            if value is not None:
                setattr(record, key, value)
        return self.nutrition_repo.update(record)

    def delete_nutrition(self, record_id: int, user_id: int) -> None:
        """Delete a nutrition record."""
        record = self.nutrition_repo.get_by_id(record_id)
        if not record:
            raise EntityNotFoundException(f"Nutrition record with ID {record_id} not found")
        if record.user_id != user_id:
            raise PermissionDeniedException("You do not have permission to delete this nutrition record")
        self.nutrition_repo.delete(record)
