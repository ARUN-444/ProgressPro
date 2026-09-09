"""
Integration tests for Daily Tracking endpoints: Weight, Sleep, and Nutrition.
"""


def test_tracking_flow_and_unique_constraints(client):
    """Test weight, sleep, and nutrition logging and verify daily uniqueness constraints."""
    # Register & login
    client.post("/api/v1/auth/register", json={"email": "tracktest@example.com", "password": "Password123!", "full_name": "Tracking Athlete"})
    login_res = client.post("/api/v1/auth/login", json={"email": "tracktest@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    test_date = "2026-09-08"

    # 1. Weight tracking
    w_payload = {"recorded_date": test_date, "weight_kg": 81.5, "body_fat_percentage": 14.8, "notes": "Fasted"}
    w_res = client.post("/api/v1/tracking/weight", json=w_payload, headers=headers)
    assert w_res.status_code == 201
    assert float(w_res.json()["weight_kg"]) == 81.5

    # Duplicate on same date should fail with 409
    dup_w = client.post("/api/v1/tracking/weight", json=w_payload, headers=headers)
    assert dup_w.status_code == 409

    # 2. Sleep tracking
    s_payload = {"recorded_date": test_date, "sleep_duration_hours": 7.8, "quality_score": 4, "resting_heart_rate": 55}
    s_res = client.post("/api/v1/tracking/sleep", json=s_payload, headers=headers)
    assert s_res.status_code == 201
    assert float(s_res.json()["sleep_duration_hours"]) == 7.8

    dup_s = client.post("/api/v1/tracking/sleep", json=s_payload, headers=headers)
    assert dup_s.status_code == 409

    # 3. Nutrition tracking
    n_payload = {"recorded_date": test_date, "calories": 2800, "protein": 180.0, "carbs": 320.0, "fats": 70.0, "water": 3.5}
    n_res = client.post("/api/v1/tracking/nutrition", json=n_payload, headers=headers)
    assert n_res.status_code == 201
    assert n_res.json()["calories"] == 2800

    dup_n = client.post("/api/v1/tracking/nutrition", json=n_payload, headers=headers)
    assert dup_n.status_code == 409

    # 4. Query histories
    assert len(client.get("/api/v1/tracking/weight", headers=headers).json()) >= 1
    assert len(client.get("/api/v1/tracking/sleep", headers=headers).json()) >= 1
    assert len(client.get("/api/v1/tracking/nutrition", headers=headers).json()) >= 1
