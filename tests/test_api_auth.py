"""
Integration tests for Authentication and User management API endpoints.
"""


def test_auth_registration_and_login_flow(client):
    """Test user registration, duplicate email rejection, and login token issuance."""
    reg_payload = {
        "email": "testathlete@example.com",
        "password": "StrongPassword123!",
        "full_name": "Marcus Aurelius",
    }
    # 1. Register
    reg_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_res.status_code == 201, reg_res.text
    reg_data = reg_res.json()
    assert reg_data["email"] == "testathlete@example.com"
    assert "hashed_password" not in reg_data

    # 2. Duplicate registration should fail
    dup_res = client.post("/api/v1/auth/register", json=reg_payload)
    assert dup_res.status_code == 409

    # 3. Login with wrong password
    wrong_login = client.post("/api/v1/auth/login", json={"email": "testathlete@example.com", "password": "WrongPassword"})
    assert wrong_login.status_code == 401

    # 4. Login with correct password
    login_res = client.post("/api/v1/auth/login", json={"email": "testathlete@example.com", "password": "StrongPassword123!"})
    assert login_res.status_code == 200
    token_data = login_res.json()
    assert "access_token" in token_data
    assert "refresh_token" in token_data

    access_token = token_data["access_token"]
    refresh_token = token_data["refresh_token"]

    # 5. Access /users/me
    headers = {"Authorization": f"Bearer {access_token}"}
    me_res = client.get("/api/v1/users/me", headers=headers)
    assert me_res.status_code == 200
    assert me_res.json()["email"] == "testathlete@example.com"

    # 6. Update user
    update_res = client.put("/api/v1/users/me", json={"full_name": "Marcus Emperor"}, headers=headers)
    assert update_res.status_code == 200
    assert update_res.json()["full_name"] == "Marcus Emperor"

    # 7. Refresh token
    refresh_res = client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_res.status_code == 200
    assert "access_token" in refresh_res.json()
