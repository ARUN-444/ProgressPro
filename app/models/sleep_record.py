"""
SleepRecord database model.
Tracks daily sleep duration, subjective quality score, and optional resting heart rate.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Date, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class SleepRecord(Base):
    """
    Sleep records table.
    Stores daily sleep recovery data used in fatigue and deload analysis.
    Enforces one entry per user per calendar day.
    """
    __tablename__ = "sleep_records"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    sleep_duration_hours: Mapped[Decimal] = mapped_column(Numeric(4, 2), nullable=False)
    quality_score: Mapped[int] = mapped_column(Integer, nullable=False)
    resting_heart_rate: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_date", name="uq_sleep_records_user_date"),
        Index("ix_sleep_records_user_date", "user_id", "recorded_date"),
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="sleep_records")

    def __repr__(self) -> str:
        return (
            f"<SleepRecord id={self.id} user_id={self.user_id} "
            f"date='{self.recorded_date}' hours={self.sleep_duration_hours}>"
        )
