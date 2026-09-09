"""
Pytest configuration and shared test fixtures for ProgressPro test suite.
Configures SQLite in-memory database with StaticPool for cross-thread test client execution.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base, get_db
from app.main import app

# Create in-memory SQLite engine with StaticPool so all threads share the same in-memory DB
TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=TEST_ENGINE)


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Create all tables before test run and clean up after."""
    Base.metadata.create_all(TEST_ENGINE)
    yield
    Base.metadata.drop_all(TEST_ENGINE)


@pytest.fixture
def db():
    """Provides a transactional database session for tests."""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def client(db):
    """Provides a FastAPI TestClient with database dependency overridden."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()
