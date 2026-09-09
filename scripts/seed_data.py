"""
ProgressPro Database Seeding Script.
Populates the database with:
1. Default standard exercise catalog (Chest, Back, Legs, Shoulders, Arms, Core)
2. Demo user account (demo@progresspro.com / Password123!)
3. Athlete fitness profile
4. 4 weeks of realistic workout history demonstrating progressive overload
5. Daily body weight tracking logs
6. Daily sleep and recovery tracking logs
7. Daily nutrition and macronutrient logs
"""

import sys
from pathlib import Path

# Add project root directory to sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings
from app.core.database import Base
from app.core.security import hash_password
from app.models.exercise import Exercise
from app.models.fitness_profile import FitnessProfile
from app.models.nutrition_record import NutritionRecord
from app.models.sleep_record import SleepRecord
from app.models.user import User
from app.models.weight_record import WeightRecord
from app.models.workout import ExerciseSet, Workout, WorkoutExercise


STANDARD_EXERCISES = [
    # Chest
    {"name": "Barbell Bench Press", "category": "barbell", "primary_muscle_group": "chest", "secondary_muscle_group": "triceps", "mechanics": "compound"},
    {"name": "Incline Dumbbell Press", "category": "dumbbell", "primary_muscle_group": "chest", "secondary_muscle_group": "shoulders", "mechanics": "compound"},
    {"name": "Cable Chest Flyes", "category": "cable", "primary_muscle_group": "chest", "secondary_muscle_group": None, "mechanics": "isolation"},
    # Back
    {"name": "Conventional Deadlift", "category": "barbell", "primary_muscle_group": "back", "secondary_muscle_group": "hamstrings", "mechanics": "compound"},
    {"name": "Barbell Bent-Over Row", "category": "barbell", "primary_muscle_group": "back", "secondary_muscle_group": "biceps", "mechanics": "compound"},
    {"name": "Neutral Grip Pull-up", "category": "bodyweight", "primary_muscle_group": "back", "secondary_muscle_group": "biceps", "mechanics": "compound"},
    {"name": "Seated Cable Row", "category": "cable", "primary_muscle_group": "back", "secondary_muscle_group": "biceps", "mechanics": "compound"},
    # Legs (Quads / Hamstrings / Glutes)
    {"name": "Barbell Back Squat", "category": "barbell", "primary_muscle_group": "quadriceps", "secondary_muscle_group": "glutes", "mechanics": "compound"},
    {"name": "Romanian Deadlift", "category": "barbell", "primary_muscle_group": "hamstrings", "secondary_muscle_group": "glutes", "mechanics": "compound"},
    {"name": "Leg Press", "category": "machine", "primary_muscle_group": "quadriceps", "secondary_muscle_group": "glutes", "mechanics": "compound"},
    {"name": "Lying Hamstring Curl", "category": "machine", "primary_muscle_group": "hamstrings", "secondary_muscle_group": None, "mechanics": "isolation"},
    {"name": "Standing Calf Raise", "category": "machine", "primary_muscle_group": "calves", "secondary_muscle_group": None, "mechanics": "isolation"},
    # Shoulders
    {"name": "Overhead Barbell Press", "category": "barbell", "primary_muscle_group": "shoulders", "secondary_muscle_group": "triceps", "mechanics": "compound"},
    {"name": "Dumbbell Lateral Raise", "category": "dumbbell", "primary_muscle_group": "shoulders", "secondary_muscle_group": None, "mechanics": "isolation"},
    {"name": "Face Pulls", "category": "cable", "primary_muscle_group": "shoulders", "secondary_muscle_group": "back", "mechanics": "isolation"},
    # Arms
    {"name": "Incline Dumbbell Curl", "category": "dumbbell", "primary_muscle_group": "biceps", "secondary_muscle_group": None, "mechanics": "isolation"},
    {"name": "Triceps Rope Pushdown", "category": "cable", "primary_muscle_group": "triceps", "secondary_muscle_group": None, "mechanics": "isolation"},
]


def seed_database(db: Session) -> None:
    print("=" * 60)
    print("Starting ProgressPro database seeding...")
    print("=" * 60)

    # 1. Seed Exercise Catalog
    exercise_map = {}
    for ex_data in STANDARD_EXERCISES:
        existing = db.query(Exercise).filter(Exercise.name == ex_data["name"]).first()
        if not existing:
            ex = Exercise(**ex_data, is_custom=False)
            db.add(ex)
            db.flush()
            exercise_map[ex.name] = ex
            print(f"Added exercise: {ex.name} ({ex.primary_muscle_group})")
        else:
            exercise_map[existing.name] = existing

    # 2. Seed Demo User
    demo_email = "demo@progresspro.com"
    demo_user = db.query(User).filter(User.email == demo_email).first()
    if not demo_user:
        demo_user = User(
            email=demo_email,
            hashed_password=hash_password("Password123!"),
            full_name="Marcus Vance",
            is_active=True,
        )
        db.add(demo_user)
        db.flush()
        print(f"Created demo user: {demo_user.email} (Password: Password123!)")
    else:
        print(f"Found existing demo user: {demo_user.email}")

    # 3. Seed Fitness Profile
    if not demo_user.profile:
        profile = FitnessProfile(
            user_id=demo_user.id,
            gender="male",
            date_of_birth=date(1998, 6, 14),
            height_cm=Decimal("182.50"),
            experience_level="intermediate",
            primary_goal="hypertrophy",
            target_weight_kg=Decimal("84.00"),
            activity_level="moderately_active",
        )
        db.add(profile)
        db.flush()
        print("Created fitness profile for Marcus Vance (Goal: Hypertrophy, Height: 182.5cm)")

    # 4. Seed Multi-Week Workout Sessions (Demonstrating Progressive Overload)
    today = date.today()
    bench = exercise_map["Barbell Bench Press"]
    squat = exercise_map["Barbell Back Squat"]
    deadlift = exercise_map["Conventional Deadlift"]
    row = exercise_map["Barbell Bent-Over Row"]
    ohp = exercise_map["Overhead Barbell Press"]

    # Week 1 to Week 4 progression schedule (3 workouts per week: Push, Pull, Legs)
    progression = [
        # (days_ago, title, exercise, [(weight, reps, rpe), ...])
        (25, "Push Day A", bench, [(Decimal("80.00"), 8, Decimal("7.5")), (Decimal("80.00"), 8, Decimal("8.0")), (Decimal("80.00"), 7, Decimal("8.5"))]),
        (23, "Pull Day A", deadlift, [(Decimal("120.00"), 5, Decimal("7.0")), (Decimal("120.00"), 5, Decimal("7.5")), (Decimal("120.00"), 5, Decimal("8.0"))]),
        (21, "Leg Day A", squat, [(Decimal("100.00"), 6, Decimal("7.5")), (Decimal("100.00"), 6, Decimal("8.0")), (Decimal("100.00"), 6, Decimal("8.5"))]),

        (18, "Push Day A", bench, [(Decimal("82.50"), 8, Decimal("8.0")), (Decimal("82.50"), 8, Decimal("8.0")), (Decimal("82.50"), 7, Decimal("8.5"))]),
        (16, "Pull Day A", deadlift, [(Decimal("125.00"), 5, Decimal("7.5")), (Decimal("125.00"), 5, Decimal("8.0")), (Decimal("125.00"), 5, Decimal("8.5"))]),
        (14, "Leg Day A", squat, [(Decimal("102.50"), 6, Decimal("8.0")), (Decimal("102.50"), 6, Decimal("8.0")), (Decimal("102.50"), 6, Decimal("8.5"))]),

        (11, "Push Day A", bench, [(Decimal("85.00"), 8, Decimal("8.0")), (Decimal("85.00"), 8, Decimal("8.5")), (Decimal("85.00"), 8, Decimal("9.0"))]),
        (9, "Pull Day A", deadlift, [(Decimal("130.00"), 5, Decimal("8.0")), (Decimal("130.00"), 5, Decimal("8.5")), (Decimal("130.00"), 5, Decimal("9.0"))]),
        (7, "Leg Day A", squat, [(Decimal("105.00"), 6, Decimal("8.0")), (Decimal("105.00"), 6, Decimal("8.5")), (Decimal("105.00"), 6, Decimal("9.0"))]),

        (4, "Push Day A", bench, [(Decimal("87.50"), 8, Decimal("8.5")), (Decimal("87.50"), 7, Decimal("9.0")), (Decimal("87.50"), 7, Decimal("9.5"))]),
        (2, "Pull Day A", deadlift, [(Decimal("135.00"), 5, Decimal("8.5")), (Decimal("135.00"), 5, Decimal("9.0")), (Decimal("135.00"), 5, Decimal("9.5"))]),
        (1, "Leg Day A", squat, [(Decimal("107.50"), 6, Decimal("8.5")), (Decimal("107.50"), 6, Decimal("9.0")), (Decimal("107.50"), 5, Decimal("9.5"))]),
    ]

    for days_ago, title, target_ex, sets_data in progression:
        w_date = today - timedelta(days=days_ago)
        existing_w = db.query(Workout).filter(Workout.user_id == demo_user.id, Workout.workout_date == w_date).first()
        if not existing_w:
            w = Workout(
                user_id=demo_user.id,
                title=title,
                workout_date=w_date,
                duration_minutes=60,
                rpe=Decimal("8.0"),
                notes="Structured progressive overload session",
            )
            we = WorkoutExercise(
                exercise_id=target_ex.id,
                order=1,
                notes="Working sets",
            )
            for set_no, (wt, rps, rpe_val) in enumerate(sets_data, start=1):
                es = ExerciseSet(
                    set_number=set_no,
                    set_type="normal",
                    weight_kg=wt,
                    reps=rps,
                    rpe=rpe_val,
                    is_completed=True,
                )
                we.exercise_sets.append(es)
            w.workout_exercises.append(we)
            db.add(w)
            print(f"Logged workout '{title}' on {w_date} with {target_ex.name}")

    # 5. Seed Daily Weight, Sleep, and Nutrition Records (Last 14 days)
    for day_offset in range(14, -1, -1):
        rec_date = today - timedelta(days=day_offset)

        # Weight log
        weight_val = Decimal("80.50") + Decimal(str((14 - day_offset) * 0.05))
        if not db.query(WeightRecord).filter(WeightRecord.user_id == demo_user.id, WeightRecord.recorded_date == rec_date).first():
            db.add(WeightRecord(
                user_id=demo_user.id,
                recorded_date=rec_date,
                weight_kg=weight_val.quantize(Decimal("0.01")),
                body_fat_percentage=Decimal("15.2"),
                notes="Morning fasted weigh-in",
            ))

        # Sleep log
        sleep_hrs = Decimal("7.5") if day_offset % 3 != 0 else Decimal("6.2")
        quality = 4 if sleep_hrs >= Decimal("7.0") else 2
        if not db.query(SleepRecord).filter(SleepRecord.user_id == demo_user.id, SleepRecord.recorded_date == rec_date).first():
            db.add(SleepRecord(
                user_id=demo_user.id,
                recorded_date=rec_date,
                sleep_duration_hours=sleep_hrs,
                quality_score=quality,
                resting_heart_rate=56,
                notes="Tracked sleep session",
            ))

        # Nutrition log
        cals = 2800 if day_offset % 2 == 0 else 2650
        prot = Decimal("175.0")
        if not db.query(NutritionRecord).filter(NutritionRecord.user_id == demo_user.id, NutritionRecord.recorded_date == rec_date).first():
            db.add(NutritionRecord(
                user_id=demo_user.id,
                recorded_date=rec_date,
                calories=cals,
                protein=prot,
                carbs=Decimal("330.0"),
                fats=Decimal("70.0"),
                water=Decimal("3.5"),
            ))

    db.commit()
    print("=" * 60)
    print("Database seeding completed successfully!")
    print(f"Demo Credentials: {demo_email} / Password123!")
    print("=" * 60)


def main():
    db_uri = settings.SQLALCHEMY_DATABASE_URI
    print(f"Connecting to database: {db_uri}")
    connect_args = {}
    if db_uri.startswith("sqlite"):
        connect_args["check_same_thread"] = False

    engine = create_engine(db_uri, connect_args=connect_args)
    # Ensure tables exist (useful for SQLite or initial setup)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()
