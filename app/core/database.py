"""
Database configuration module using SQLAlchemy 2.0 style.
Configures database engine, session factory, base model class, and dependency injection.
"""

from typing import Generator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker, Session, DeclarativeBase
from app.core.config import settings
from app.core.logging import logger

# Configure connection arguments based on database dialect
db_uri = settings.SQLALCHEMY_DATABASE_URI
connect_args = {}

# SQLite requires check_same_thread=False for multi-threaded access in FastAPI
if db_uri.startswith("sqlite"):
    connect_args["check_same_thread"] = False

from sqlalchemy import event

# Create SQLAlchemy 2.0 Engine
# pool_pre_ping=True tests connections before using them, preventing stale MySQL connection errors
engine = create_engine(
    db_uri,
    connect_args=connect_args,
    pool_pre_ping=True,
    pool_recycle=3600,
    echo=settings.DEBUG,
)

if db_uri.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

# Session factory for generating new database sessions
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """
    SQLAlchemy 2.0 Declarative Base class.
    All ORM models in Phase 2 will inherit from this class.
    """
    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a transactional database session per request.
    Automatically closes the session after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def check_database_connection() -> bool:
    """
    Executes a simple SELECT 1 query to verify database connectivity.
    Returns True if healthy, False otherwise.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database connection check failed: %s", exc)
        return False
