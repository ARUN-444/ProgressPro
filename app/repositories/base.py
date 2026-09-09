"""
Generic Base Repository providing standardized SQLAlchemy 2.0 CRUD operations.
"""

from typing import Generic, Optional, Sequence, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.orm import Session

ModelType = TypeVar("ModelType")


class BaseRepository(Generic[ModelType]):
    """
    Generic Base Repository providing fundamental CRUD operations.
    Uses pure SQLAlchemy 2.0 style queries.
    """

    def __init__(self, model: Type[ModelType], db: Session):
        self.model = model
        self.db = db

    def get_by_id(self, id: int) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        return self.db.get(self.model, id)

    def get_all(self, skip: int = 0, limit: int = 100) -> Sequence[ModelType]:
        """Fetch records with pagination."""
        stmt = select(self.model).offset(skip).limit(limit)
        return self.db.scalars(stmt).all()

    def create(self, obj: ModelType) -> ModelType:
        """Add and commit a new record."""
        self.db.add(obj)
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def update(self, obj: ModelType) -> ModelType:
        """Commit updates to an existing attached record."""
        self.db.commit()
        self.db.refresh(obj)
        return obj

    def delete(self, obj: ModelType) -> None:
        """Delete an attached record from the database."""
        self.db.delete(obj)
        self.db.commit()
