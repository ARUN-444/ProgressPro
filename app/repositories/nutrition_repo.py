"""
Nutrition repository handling daily calorie, macronutrient, and hydration records.
"""

from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.nutrition_record import NutritionRecord
from app.repositories.base import BaseRepository


class NutritionRepository(BaseRepository[NutritionRecord]):
    """
    Data access layer for NutritionRecord entries.
    """

    def __init__(self, db: Session):
        super().__init__(NutritionRecord, db)

    def get_by_user_and_date(self, user_id: int, recorded_date: date) -> Optional[NutritionRecord]:
        """Fetch the nutrition entry for a user on a specific calendar date."""
        stmt = (
            select(NutritionRecord)
            .where(NutritionRecord.user_id == user_id)
            .where(NutritionRecord.recorded_date == recorded_date)
        )
        return self.db.scalars(stmt).first()

    def list_by_user(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[NutritionRecord]:
        """List historical nutrition entries for a user, ordered by date ascending."""
        stmt = select(NutritionRecord).where(NutritionRecord.user_id == user_id)

        if start_date:
            stmt = stmt.where(NutritionRecord.recorded_date >= start_date)
        if end_date:
            stmt = stmt.where(NutritionRecord.recorded_date <= end_date)

        stmt = stmt.order_by(NutritionRecord.recorded_date.desc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()
