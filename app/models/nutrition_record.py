"""
NutritionRecord database model.
Tracks daily total calories, macronutrients (protein, carbs, fats), and water intake.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Date, ForeignKey, Index, Integer, Numeric, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class NutritionRecord(Base):
    """
    Nutrition records table.
    Stores daily aggregated calories and macronutrient intake for energy balance and protein rules.
    Enforces one entry per user per calendar day.
    """
    __tablename__ = "nutrition_records"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    recorded_date: Mapped[date] = mapped_column(Date, nullable=False)
    calories: Mapped[int] = mapped_column(Integer, nullable=False)
    protein: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    carbs: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    fats: Mapped[Decimal] = mapped_column(Numeric(5, 1), nullable=False)
    water: Mapped[Optional[Decimal]] = mapped_column(Numeric(4, 2), nullable=True)

    # Constraints and indexes
    __table_args__ = (
        UniqueConstraint("user_id", "recorded_date", name="uq_nutrition_records_user_date"),
        Index("ix_nutrition_records_user_date", "user_id", "recorded_date"),
    )

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="nutrition_records")

    def __repr__(self) -> str:
        return (
            f"<NutritionRecord id={self.id} user_id={self.user_id} "
            f"date='{self.recorded_date}' calories={self.calories}>"
        )
