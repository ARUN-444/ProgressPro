"""
FitnessProfile database model.
Stores user demographic and baseline fitness attributes required for metabolic and volume calculations.
"""

from datetime import date
from decimal import Decimal
from typing import Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User


class FitnessProfile(Base):
    """
    Fitness profile table.
    One-to-one relationship with the users table.
    """
    __tablename__ = "fitness_profiles"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    gender: Mapped[str] = mapped_column(String(20), nullable=False)
    date_of_birth: Mapped[date] = mapped_column(Date, nullable=False)
    height_cm: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    experience_level: Mapped[str] = mapped_column(String(20), nullable=False)
    primary_goal: Mapped[str] = mapped_column(String(30), nullable=False)
    target_weight_kg: Mapped[Optional[Decimal]] = mapped_column(Numeric(5, 2), nullable=True)
    activity_level: Mapped[str] = mapped_column(String(30), nullable=False)

    # Relationship back to User
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __repr__(self) -> str:
        return f"<FitnessProfile id={self.id} user_id={self.user_id} goal='{self.primary_goal}'>"
