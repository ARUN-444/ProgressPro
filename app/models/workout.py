"""
Workout database models.
Contains the nested workout tracking hierarchy:
Workout -> WorkoutExercise -> ExerciseSet.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.exercise import Exercise


class Workout(Base):
    """
    Workout session table.
    Represents an individual training session completed by a user.
    """
    __tablename__ = "workouts"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(150), nullable=False)
    workout_date: Mapped[date] = mapped_column(Date, nullable=False)
    start_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    end_time: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    duration_minutes: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    rpe: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Composite index on user_id and workout_date for fast time-series filtering
    __table_args__ = (
        Index("ix_workouts_user_id_workout_date", "user_id", "workout_date"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="workouts")
    workout_exercises: Mapped[List["WorkoutExercise"]] = relationship(
        "WorkoutExercise",
        back_populates="workout",
        cascade="all, delete-orphan",
        order_by="WorkoutExercise.order",
    )

    def __repr__(self) -> str:
        return f"<Workout id={self.id} user_id={self.user_id} title='{self.title}' date='{self.workout_date}'>"


class WorkoutExercise(Base):
    """
    WorkoutExercise junction table.
    Connects a Workout to an Exercise, tracking the order and notes for that movement.
    """
    __tablename__ = "workout_exercises"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    workout_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workouts.id", ondelete="CASCADE"),
        nullable=False,
    )
    exercise_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("exercises.id", ondelete="RESTRICT"),
        nullable=False,
    )
    # Using column name "order" with attribute name order
    order: Mapped[int] = mapped_column("order", Integer, default=1, nullable=False)
    notes: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relationships
    workout: Mapped["Workout"] = relationship("Workout", back_populates="workout_exercises")
    exercise: Mapped["Exercise"] = relationship("Exercise", back_populates="workout_exercises")
    exercise_sets: Mapped[List["ExerciseSet"]] = relationship(
        "ExerciseSet",
        back_populates="workout_exercise",
        cascade="all, delete-orphan",
        order_by="ExerciseSet.set_number",
    )

    def __repr__(self) -> str:
        return f"<WorkoutExercise id={self.id} workout_id={self.workout_id} exercise_id={self.exercise_id} order={self.order}>"


class ExerciseSet(Base):
    """
    ExerciseSet table.
    Tracks individual set performance: set number, type, load (kg), reps, and RPE.
    """
    __tablename__ = "exercise_sets"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    workout_exercise_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("workout_exercises.id", ondelete="CASCADE"),
        nullable=False,
    )
    set_number: Mapped[int] = mapped_column(Integer, nullable=False)
    set_type: Mapped[str] = mapped_column(String(20), default="normal", nullable=False)
    weight_kg: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0.00"), nullable=False)
    reps: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    rpe: Mapped[Optional[Decimal]] = mapped_column(Numeric(3, 1), nullable=True)
    is_completed: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationship back to parent WorkoutExercise
    workout_exercise: Mapped["WorkoutExercise"] = relationship(
        "WorkoutExercise",
        back_populates="exercise_sets",
    )

    def __repr__(self) -> str:
        return (
            f"<ExerciseSet id={self.id} set_number={self.set_number} "
            f"weight={self.weight_kg}kg reps={self.reps}>"
        )
