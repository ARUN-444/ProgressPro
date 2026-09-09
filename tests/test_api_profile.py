"""
Integration tests for Fitness Profile API endpoints.
"""


def test_fitness_profile_flow(client):
    """Test creating, fetching, and updating a fitness profile."""
    # 1. Register & login
    client.post("/api/v1/auth/register", json={"email": "profileuser@example.com", "password": "Password123!", "full_name": "Profile Athlete"})
    login_res = client.post("/api/v1/auth/login", json={"email": "profileuser@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Get profile before creation should return 404
    get_before = client.get("/api/v1/profile", headers=headers)
    assert get_before.status_code == 404

    # 3. Create profile
    create_payload = {
        "gender": "male",
        "date_of_birth": "1997-04-12",
        "height_cm": 181.0,
        "experience_level": "intermediate",
        "primary_goal": "hypertrophy",
        "target_weight_kg": 82.5,
        "activity_level": "moderately_active",
    }
    create_res = client.post("/api/v1/profile", json=create_payload, headers=headers)
    assert create_res.status_code == 201
    assert create_res.json()["primary_goal"] == "hypertrophy"

    # 4. Duplicate creation should fail with 409
    dup_res = client.post("/api/v1/profile", json=create_payload, headers=headers)
    assert dup_res.status_code == 409

    # 5. Get profile
    get_res = client.get("/api/v1/profile", headers=headers)
    assert get_res.status_code == 200
    assert float(get_res.json()["height_cm"]) == 181.0

    # 6. Update profile
    update_res = client.put("/api/v1/profile", json={"primary_goal": "strength"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["primary_goal"] == "strength"
