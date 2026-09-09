"""
User database model.
Represents an athlete/user account with authentication credentials and relationships to all tracking entities.
"""

from datetime import datetime
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.fitness_profile import FitnessProfile
    from app.models.workout import Workout
    from app.models.exercise import Exercise
    from app.models.weight_record import WeightRecord
    from app.models.sleep_record import SleepRecord
    from app.models.nutrition_record import NutritionRecord


class User(Base):
    """
    Users table.
    Stores core identity and credentials.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    # Relationships
    # One-to-one relationship with FitnessProfile (uselist=False)
    profile: Mapped[Optional["FitnessProfile"]] = relationship(
        "FitnessProfile",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )

    # One-to-many relationships with tracking entities (cascade delete if user is deleted)
    workouts: Mapped[List["Workout"]] = relationship(
        "Workout",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    weight_records: Mapped[List["WeightRecord"]] = relationship(
        "WeightRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    sleep_records: Mapped[List["SleepRecord"]] = relationship(
        "SleepRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    nutrition_records: Mapped[List["NutritionRecord"]] = relationship(
        "NutritionRecord",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    custom_exercises: Mapped[List["Exercise"]] = relationship(
        "Exercise",
        back_populates="created_by_user",
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} email='{self.email}' full_name='{self.full_name}'>"
