"""
Exercise database model.
Contains the standardized exercise library and custom user-created exercises.
"""

from typing import List, Optional, TYPE_CHECKING
from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.database import Base

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workout import WorkoutExercise


class Exercise(Base):
    """
    Exercise table.
    Catalog of movements categorized by primary and secondary muscle groups.
    """
    __tablename__ = "exercises"

    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(150), unique=True, index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False)
    primary_muscle_group: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    secondary_muscle_group: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    mechanics: Mapped[str] = mapped_column(String(30), nullable=False)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_by_user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    workout_exercises: Mapped[List["WorkoutExercise"]] = relationship(
        "WorkoutExercise",
        back_populates="exercise",
    )
    created_by_user: Mapped[Optional["User"]] = relationship(
        "User",
        back_populates="custom_exercises",
    )

    def __repr__(self) -> str:
        return f"<Exercise id={self.id} name='{self.name}' primary_muscle='{self.primary_muscle_group}'>"
