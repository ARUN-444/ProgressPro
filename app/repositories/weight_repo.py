"""
Weight repository handling daily weight and body fat records.
"""

from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.weight_record import WeightRecord
from app.repositories.base import BaseRepository


class WeightRepository(BaseRepository[WeightRecord]):
    """
    Data access layer for WeightRecord entries.
    """

    def __init__(self, db: Session):
        super().__init__(WeightRecord, db)

    def get_by_user_and_date(self, user_id: int, recorded_date: date) -> Optional[WeightRecord]:
        """Fetch the weight entry for a user on a specific calendar date."""
        stmt = (
            select(WeightRecord)
            .where(WeightRecord.user_id == user_id)
            .where(WeightRecord.recorded_date == recorded_date)
        )
        return self.db.scalars(stmt).first()

    def get_latest_by_user(self, user_id: int) -> Optional[WeightRecord]:
        """Fetch the most recent weight record for an athlete."""
        stmt = (
            select(WeightRecord)
            .where(WeightRecord.user_id == user_id)
            .order_by(WeightRecord.recorded_date.desc())
            .limit(1)
        )
        return self.db.scalars(stmt).first()

    def list_by_user(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[WeightRecord]:
        """List historical weight entries for a user, ordered by date descending."""
        stmt = select(WeightRecord).where(WeightRecord.user_id == user_id)

        if start_date:
            stmt = stmt.where(WeightRecord.recorded_date >= start_date)
        if end_date:
            stmt = stmt.where(WeightRecord.recorded_date <= end_date)

        stmt = stmt.order_by(WeightRecord.recorded_date.desc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()
