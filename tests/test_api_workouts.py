"""
Integration tests for Exercises and Workout tracking API endpoints.
"""


def test_workout_and_exercise_tracking_flow(client):
    """Test custom exercise creation and nested workout session logging."""
    # 1. Register & login
    client.post("/api/v1/auth/register", json={"email": "workoutathlete@example.com", "password": "Password123!", "full_name": "Workout Athlete"})
    login_res = client.post("/api/v1/auth/login", json={"email": "workoutathlete@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create an exercise
    ex_payload = {
        "name": "Incline Dumbbell Flyes",
        "category": "dumbbell",
        "primary_muscle_group": "chest",
        "secondary_muscle_group": None,
        "mechanics": "isolation",
        "is_custom": True,
    }
    ex_res = client.post("/api/v1/exercises", json=ex_payload, headers=headers)
    assert ex_res.status_code == 201
    exercise_id = ex_res.json()["id"]

    # 3. List exercises
    list_res = client.get("/api/v1/exercises?primary_muscle_group=chest", headers=headers)
    assert list_res.status_code == 200
    assert any(e["id"] == exercise_id for e in list_res.json())

    # 4. Log a workout session with nested sets
    workout_payload = {
        "title": "Chest & Triceps Hypertrophy",
        "workout_date": "2026-09-08",
        "duration_minutes": 55,
        "rpe": 8.0,
        "notes": "Solid pump, controlled negatives",
        "workout_exercises": [
            {
                "exercise_id": exercise_id,
                "order": 1,
                "notes": "Felt good stretch",
                "exercise_sets": [
                    {"set_number": 1, "set_type": "normal", "weight_kg": 20.0, "reps": 10, "rpe": 7.5, "is_completed": True},
                    {"set_number": 2, "set_type": "normal", "weight_kg": 22.5, "reps": 8, "rpe": 8.5, "is_completed": True},
                ],
            }
        ],
    }
    w_res = client.post("/api/v1/workouts", json=workout_payload, headers=headers)
    assert w_res.status_code == 201
    w_data = w_res.json()
    assert w_data["title"] == "Chest & Triceps Hypertrophy"
    assert len(w_data["workout_exercises"]) == 1
    assert len(w_data["workout_exercises"][0]["exercise_sets"]) == 2

    workout_id = w_data["id"]

    # 5. Get workout by ID
    get_w = client.get(f"/api/v1/workouts/{workout_id}", headers=headers)
    assert get_w.status_code == 200
    assert get_w.json()["id"] == workout_id

    # 6. List workouts
    list_w = client.get("/api/v1/workouts", headers=headers)
    assert list_w.status_code == 200
    assert len(list_w.json()) >= 1
