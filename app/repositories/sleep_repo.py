"""
Sleep repository handling daily sleep logs and recovery metrics.
"""

from datetime import date
from typing import Optional, Sequence
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.sleep_record import SleepRecord
from app.repositories.base import BaseRepository


class SleepRepository(BaseRepository[SleepRecord]):
    """
    Data access layer for SleepRecord entries.
    """

    def __init__(self, db: Session):
        super().__init__(SleepRecord, db)

    def get_by_user_and_date(self, user_id: int, recorded_date: date) -> Optional[SleepRecord]:
        """Fetch the sleep log for a user on a specific calendar date."""
        stmt = (
            select(SleepRecord)
            .where(SleepRecord.user_id == user_id)
            .where(SleepRecord.recorded_date == recorded_date)
        )
        return self.db.scalars(stmt).first()

    def list_by_user(
        self,
        user_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> Sequence[SleepRecord]:
        """List historical sleep logs for a user, ordered by date ascending."""
        stmt = select(SleepRecord).where(SleepRecord.user_id == user_id)

        if start_date:
            stmt = stmt.where(SleepRecord.recorded_date >= start_date)
        if end_date:
            stmt = stmt.where(SleepRecord.recorded_date <= end_date)

        stmt = stmt.order_by(SleepRecord.recorded_date.desc()).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()
