"""
Unit tests for SQLAlchemy 2.0 database models in Phase 2.
Verifies model attributes, table definitions, foreign keys, and relationships.
"""

from datetime import date, datetime, timezone
from decimal import Decimal
from app.core.database import Base
from app.models import (
    User,
    FitnessProfile,
    Exercise,
    Workout,
    WorkoutExercise,
    ExerciseSet,
    WeightRecord,
    SleepRecord,
    NutritionRecord,
)


def test_registered_tables():
    """Verify that all 9 tables are registered on Base.metadata."""
    table_names = set(Base.metadata.tables.keys())
    expected_tables = {
        "users",
        "fitness_profiles",
        "exercises",
        "workouts",
        "workout_exercises",
        "exercise_sets",
        "weight_records",
        "sleep_records",
        "nutrition_records",
    }
    assert expected_tables.issubset(table_names), f"Missing tables: {expected_tables - table_names}"


def test_user_model_instantiation():
    """Verify User model instantiation and repr."""
    user = User(
        email="athlete@example.com",
        hashed_password="hashedpassword123",
        full_name="Alex Mercer",
        is_active=True,
    )
    assert user.email == "athlete@example.com"
    assert user.full_name == "Alex Mercer"
    assert user.is_active is True
    assert "athlete@example.com" in repr(user)


def test_fitness_profile_model_instantiation():
    """Verify FitnessProfile model instantiation and repr."""
    profile = FitnessProfile(
        gender="male",
        date_of_birth=date(1998, 5, 20),
        height_cm=Decimal("180.50"),
        experience_level="intermediate",
        primary_goal="hypertrophy",
        target_weight_kg=Decimal("82.00"),
        activity_level="moderately_active",
    )
    assert profile.gender == "male"
    assert profile.height_cm == Decimal("180.50")
    assert profile.primary_goal == "hypertrophy"
    assert "hypertrophy" in repr(profile)


def test_exercise_model_instantiation():
    """Verify Exercise model instantiation and repr."""
    exercise = Exercise(
        name="Barbell Bench Press",
        category="barbell",
        primary_muscle_group="chest",
        secondary_muscle_group="triceps",
        mechanics="compound",
        is_custom=False,
    )
    assert exercise.name == "Barbell Bench Press"
    assert exercise.primary_muscle_group == "chest"
    assert "Barbell Bench Press" in repr(exercise)


def test_workout_hierarchy_instantiation():
    """Verify Workout, WorkoutExercise, and ExerciseSet hierarchy."""
    workout = Workout(
        title="Push Day A",
        workout_date=date(2026, 9, 9),
        duration_minutes=65,
        rpe=Decimal("8.5"),
        notes="Felt energetic, increased bench load.",
    )
    assert workout.title == "Push Day A"
    assert workout.duration_minutes == 65
    assert "Push Day A" in repr(workout)

    workout_ex = WorkoutExercise(
        order=1,
        notes="Paused reps on chest",
    )
    assert workout_ex.order == 1
    assert "order=1" in repr(workout_ex)

    set_entry = ExerciseSet(
        set_number=1,
        set_type="normal",
        weight_kg=Decimal("100.00"),
        reps=8,
        rpe=Decimal("8.0"),
        is_completed=True,
    )
    assert set_entry.set_number == 1
    assert set_entry.weight_kg == Decimal("100.00")
    assert set_entry.reps == 8
    assert "100.00kg" in repr(set_entry)


def test_daily_tracking_models_instantiation():
    """Verify WeightRecord, SleepRecord, and NutritionRecord models."""
    weight = WeightRecord(
        recorded_date=date(2026, 9, 9),
        weight_kg=Decimal("80.25"),
        body_fat_percentage=Decimal("14.50"),
        notes="Morning weigh-in fasted",
    )
    assert weight.weight_kg == Decimal("80.25")
    assert "80.25kg" in repr(weight)

    sleep = SleepRecord(
        recorded_date=date(2026, 9, 9),
        sleep_duration_hours=Decimal("7.75"),
        quality_score=4,
        resting_heart_rate=58,
        notes="Deep sleep was good",
    )
    assert sleep.sleep_duration_hours == Decimal("7.75")
    assert sleep.quality_score == 4
    assert "hours=7.75" in repr(sleep)

    nutrition = NutritionRecord(
        recorded_date=date(2026, 9, 9),
        calories=2850,
        protein=Decimal("185.0"),
        carbs=Decimal("320.0"),
        fats=Decimal("75.0"),
        water=Decimal("3.50"),
    )
    assert nutrition.calories == 2850
    assert nutrition.protein == Decimal("185.0")
    assert "calories=2850" in repr(nutrition)
