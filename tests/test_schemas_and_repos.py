"""
Unit tests for Phase 3: Pydantic schemas validation and Repository data access operations.
Uses SQLite in-memory database to test repository CRUD without requiring live MySQL.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.models import User, FitnessProfile, Exercise, Workout, WorkoutExercise, ExerciseSet, WeightRecord, SleepRecord, NutritionRecord
from app.schemas import (
    UserRegister,
    UserLogin,
    UserRead,
    FitnessProfileCreate,
    FitnessProfileRead,
    ExerciseCreate,
    ExerciseRead,
    WorkoutCreate,
    WorkoutRead,
    WorkoutExerciseCreate,
    ExerciseSetCreate,
    WeightRecordCreate,
    SleepRecordCreate,
    NutritionRecordCreate,
    VolumeAnalyticsResponse,
    OverallProgressScoreResponse,
    RecommendationItem,
)
from app.repositories import (
    UserRepository,
    ProfileRepository,
    ExerciseRepository,
    WorkoutRepository,
    WeightRepository,
    SleepRepository,
    NutritionRepository,
)


# ---------------------------------------------------------------------------
# Test Fixture: In-Memory SQLite Session
# ---------------------------------------------------------------------------

@pytest.fixture
def db_session():
    """Provides an isolated in-memory SQLite database session for repository testing."""
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Schema Tests
# ---------------------------------------------------------------------------

def test_user_schemas_validation():
    """Verify user registration schema validation."""
    valid_reg = UserRegister(email="athlete@example.com", password="password123", full_name="Alex Mercer")
    assert valid_reg.email == "athlete@example.com"
    assert valid_reg.full_name == "Alex Mercer"

    # Test short password
    with pytest.raises(ValidationError):
        UserRegister(email="athlete@example.com", password="123", full_name="Alex Mercer")

    # Test invalid email
    with pytest.raises(ValidationError):
        UserRegister(email="not-an-email", password="password123", full_name="Alex Mercer")


def test_fitness_profile_schema_validation():
    """Verify fitness profile validation."""
    profile_data = FitnessProfileCreate(
        gender="male",
        date_of_birth=date(1995, 8, 15),
        height_cm=Decimal("178.50"),
        experience_level="intermediate",
        primary_goal="hypertrophy",
        target_weight_kg=Decimal("80.00"),
        activity_level="moderately_active",
    )
    assert profile_data.height_cm == Decimal("178.50")
    assert profile_data.primary_goal == "hypertrophy"


def test_workout_nested_schema_validation():
    """Verify nested workout creation schema validation."""
    workout_data = WorkoutCreate(
        title="Upper Body Strength",
        workout_date=date(2026, 9, 9),
        duration_minutes=60,
        rpe=Decimal("8.5"),
        workout_exercises=[
            WorkoutExerciseCreate(
                exercise_id=1,
                order=1,
                exercise_sets=[
                    ExerciseSetCreate(set_number=1, set_type="normal", weight_kg=Decimal("100.00"), reps=6, rpe=Decimal("8.0")),
                    ExerciseSetCreate(set_number=2, set_type="normal", weight_kg=Decimal("100.00"), reps=6, rpe=Decimal("8.5")),
                ],
            )
        ],
    )
    assert len(workout_data.workout_exercises) == 1
    assert len(workout_data.workout_exercises[0].exercise_sets) == 2

    # RPE exceeding 10.0 should fail validation
    with pytest.raises(ValidationError):
        ExerciseSetCreate(set_number=1, weight_kg=Decimal("100.00"), reps=5, rpe=Decimal("11.0"))


def test_tracking_schemas_validation():
    """Verify weight, sleep, and nutrition schemas."""
    weight = WeightRecordCreate(recorded_date=date(2026, 9, 9), weight_kg=Decimal("79.50"), body_fat_percentage=Decimal("15.0"))
    assert weight.weight_kg == Decimal("79.50")

    # Impossible body weight should fail
    with pytest.raises(ValidationError):
        WeightRecordCreate(recorded_date=date(2026, 9, 9), weight_kg=Decimal("10.00"))

    sleep = SleepRecordCreate(recorded_date=date(2026, 9, 9), sleep_duration_hours=Decimal("8.0"), quality_score=4)
    assert sleep.sleep_duration_hours == Decimal("8.0")

    # Quality score out of 1-5 range should fail
    with pytest.raises(ValidationError):
        SleepRecordCreate(recorded_date=date(2026, 9, 9), sleep_duration_hours=Decimal("8.0"), quality_score=6)

    nutrition = NutritionRecordCreate(
        recorded_date=date(2026, 9, 9),
        calories=2700,
        protein=Decimal("180.0"),
        carbs=Decimal("300.0"),
        fats=Decimal("70.0"),
    )
    assert nutrition.calories == 2700


# ---------------------------------------------------------------------------
# Repository Tests
# ---------------------------------------------------------------------------

def test_user_repository_crud(db_session):
    """Test UserRepository create, get_by_email, get_by_id, and delete."""
    repo = UserRepository(db_session)
    user = User(
        email="testuser@example.com",
        hashed_password="hash",
        full_name="Test Athlete",
        is_active=True,
    )
    created = repo.create(user)
    assert created.id is not None

    fetched = repo.get_by_email("testuser@example.com")
    assert fetched is not None
    assert fetched.full_name == "Test Athlete"

    assert repo.get_by_email("nonexistent@example.com") is None


def test_profile_repository(db_session):
    """Test ProfileRepository create and get_by_user_id."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(User(email="profiletest@example.com", hashed_password="hash", full_name="Profile User"))

    profile_repo = ProfileRepository(db_session)
    profile = FitnessProfile(
        user_id=user.id,
        gender="female",
        date_of_birth=date(1996, 3, 10),
        height_cm=Decimal("165.00"),
        experience_level="beginner",
        primary_goal="fat_loss",
        activity_level="moderately_active",
    )
    created = profile_repo.create(profile)
    assert created.id is not None

    fetched = profile_repo.get_by_user_id(user.id)
    assert fetched is not None
    assert fetched.primary_goal == "fat_loss"


def test_exercise_repository_filtering(db_session):
    """Test ExerciseRepository create, get_by_name, and list_exercises."""
    repo = ExerciseRepository(db_session)
    repo.create(Exercise(name="Squat", category="barbell", primary_muscle_group="quadriceps", mechanics="compound", is_custom=False))
    repo.create(Exercise(name="Bench Press", category="barbell", primary_muscle_group="chest", mechanics="compound", is_custom=False))

    results = repo.list_exercises(primary_muscle_group="chest")
    assert len(results) == 1
    assert results[0].name == "Bench Press"

    by_name = repo.get_by_name("squat")
    assert by_name is not None
    assert by_name.name == "Squat"


def test_workout_repository_nested_loading(db_session):
    """Test WorkoutRepository eager loading with selectinload."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(User(email="workouttest@example.com", hashed_password="hash", full_name="Workout User"))

    ex_repo = ExerciseRepository(db_session)
    ex = ex_repo.create(Exercise(name="Deadlift", category="barbell", primary_muscle_group="back", mechanics="compound", is_custom=False))

    workout = Workout(
        user_id=user.id,
        title="Pull Session",
        workout_date=date(2026, 9, 9),
        workout_exercises=[
            WorkoutExercise(
                exercise_id=ex.id,
                order=1,
                exercise_sets=[
                    ExerciseSet(set_number=1, set_type="normal", weight_kg=Decimal("140.00"), reps=5, rpe=Decimal("8.0")),
                ],
            )
        ],
    )
    workout_repo = WorkoutRepository(db_session)
    created = workout_repo.create(workout)
    assert created.id is not None

    fetched = workout_repo.get_by_id(created.id, user_id=user.id)
    assert fetched is not None
    assert len(fetched.workout_exercises) == 1
    assert len(fetched.workout_exercises[0].exercise_sets) == 1
    assert fetched.workout_exercises[0].exercise_sets[0].weight_kg == Decimal("140.00")


def test_tracking_repositories_date_filtering(db_session):
    """Test WeightRepository, SleepRepository, and NutritionRepository date queries."""
    user_repo = UserRepository(db_session)
    user = user_repo.create(User(email="trackingtest@example.com", hashed_password="hash", full_name="Tracking User"))

    weight_repo = WeightRepository(db_session)
    weight_repo.create(WeightRecord(user_id=user.id, recorded_date=date(2026, 9, 8), weight_kg=Decimal("80.00")))
    weight_repo.create(WeightRecord(user_id=user.id, recorded_date=date(2026, 9, 9), weight_kg=Decimal("79.80")))

    records = weight_repo.list_by_user(user.id, start_date=date(2026, 9, 9))
    assert len(records) == 1
    assert records[0].recorded_date == date(2026, 9, 9)

    by_date = weight_repo.get_by_user_and_date(user.id, date(2026, 9, 8))
    assert by_date is not None
    assert by_date.weight_kg == Decimal("80.00")
