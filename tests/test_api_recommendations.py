"""
Integration tests for Explainable Recommendation API endpoints.
"""


def test_recommendation_endpoints(client):
    """Verify /recommendations/fitness, /recommendations/nutrition, and /recommendations/report."""
    # Register & login
    client.post("/api/v1/auth/register", json={"email": "recsuser@example.com", "password": "Password123!", "full_name": "Recommendations Athlete"})
    login_res = client.post("/api/v1/auth/login", json={"email": "recsuser@example.com", "password": "Password123!"})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Setup profile
    client.post("/api/v1/profile", json={
        "gender": "male",
        "date_of_birth": "1998-05-10",
        "height_cm": 180.0,
        "experience_level": "intermediate",
        "primary_goal": "hypertrophy",
        "target_weight_kg": 82.0,
        "activity_level": "moderately_active",
    }, headers=headers)

    # 1. Test fitness recommendations
    fit_res = client.get("/api/v1/recommendations/fitness", headers=headers)
    assert fit_res.status_code == 200
    assert isinstance(fit_res.json(), list)

    # 2. Test nutrition recommendations
    nut_res = client.get("/api/v1/recommendations/nutrition", headers=headers)
    assert nut_res.status_code == 200
    assert isinstance(nut_res.json(), list)

    # 3. Test combined report
    report_res = client.get("/api/v1/recommendations/report", headers=headers)
    assert report_res.status_code == 200
    report_data = report_res.json()
    assert "overall_progress_score" in report_data
    assert "recommendations" in report_data
    assert isinstance(report_data["recommendations"], list)
