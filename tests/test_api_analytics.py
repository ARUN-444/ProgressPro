"""
Integration tests for Analytics API endpoints:
Volume analysis, 1RM strength trends, consistency, progressive overload, recovery, and progress score.
"""


def test_analytics_endpoints(client):
    """Verify volume, consistency, recovery, and overall progress score endpoints."""
    # Register & login
    client.post("/api/v1/auth/register", json={"email": "analyticsuser@example.com", "password": "Password123!", "full_name": "Analytics Athlete"})
    login_res = client.post("/api/v1/auth/login", json={"email": "analyticsuser@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Create exercise and log 2 workouts to test progressive overload
    ex_res = client.post(
        "/api/v1/exercises",
        json={"name": "Back Squat", "category": "barbell", "primary_muscle_group": "quadriceps", "mechanics": "compound", "is_custom": True},
        headers=headers,
    )
    exercise_id = ex_res.json()["id"]

    # Session 1: 100kg for 5 reps
    client.post("/api/v1/workouts", json={
        "title": "Leg Day 1",
        "workout_date": "2026-09-01",
        "duration_minutes": 50,
        "rpe": 8.0,
        "workout_exercises": [{
            "exercise_id": exercise_id,
            "order": 1,
            "exercise_sets": [{"set_number": 1, "set_type": "normal", "weight_kg": 100.0, "reps": 5, "rpe": 8.0, "is_completed": True}],
        }],
    }, headers=headers)

    # Session 2: 105kg for 5 reps (Demonstrating load overload!)
    client.post("/api/v1/workouts", json={
        "title": "Leg Day 2",
        "workout_date": "2026-09-08",
        "duration_minutes": 50,
        "rpe": 8.5,
        "workout_exercises": [{
            "exercise_id": exercise_id,
            "order": 1,
            "exercise_sets": [{"set_number": 1, "set_type": "normal", "weight_kg": 105.0, "reps": 5, "rpe": 8.5, "is_completed": True}],
        }],
    }, headers=headers)

    # Test Volume endpoint
    vol_res = client.get("/api/v1/analytics/volume", headers=headers)
    assert vol_res.status_code == 200
    assert vol_res.json()["total_sessions"] == 2
    assert float(vol_res.json()["total_tonnage_kg"]) > 0

    # Test Strength Progression (1RM) endpoint
    str_res = client.get(f"/api/v1/analytics/strength?exercise_id={exercise_id}", headers=headers)
    assert str_res.status_code == 200
    assert float(str_res.json()["percentage_change"]) > 0

    # Test Progressive Overload endpoint
    ov_res = client.get(f"/api/v1/analytics/progressive-overload?exercise_id={exercise_id}", headers=headers)
    assert ov_res.status_code == 200
    assert ov_res.json()["status"] == "OVERLOAD_ACHIEVED"
    assert ov_res.json()["overload_dimension"] == "LOAD_INCREASE"

    # Test Consistency endpoint
    con_res = client.get("/api/v1/analytics/consistency", headers=headers)
    assert con_res.status_code == 200
    assert con_res.json()["total_workouts_completed"] == 2

    # Test Recovery endpoint
    rec_res = client.get("/api/v1/analytics/recovery", headers=headers)
    assert rec_res.status_code == 200
    assert "recovery_score" in rec_res.json()

    # Test Progress Score endpoint
    score_res = client.get("/api/v1/analytics/progress-score", headers=headers)
    assert score_res.status_code == 200
    assert 0 <= score_res.json()["score"] <= 100
    assert "pillars" in score_res.json()
