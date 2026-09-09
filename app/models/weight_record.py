"""
WeightRecord database model.
Tracks daily body weight and optional body fat percentage logs.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Date, ForeignKey, Index, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class WeightRecord(Base):
    """
    Weight records table.
    Stores historical daily body weight entries for an athlete.
    Enforces one entry per user per calendar day.
    """
    __tablename__ = "weight_records"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    body_fat_percentage: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_date", name="uq_weight_records_user_date"),
        Index("ix_weight_records_user_date", "user_id", "recorded_date"),
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="weight_records")

    def __repr__(self) -> str:
        return f"<WeightRecord id={self.id} user_id={self.user_id} date='{self.recorded_date}' weight={self.weight_kg}kg>"
