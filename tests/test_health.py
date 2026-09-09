"""
Health check and basic configuration tests for ProgressPro Phase 1.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.core.config import settings
from app.core.security import hash_password, verify_password, create_access_token, decode_token

client = TestClient(app)


def test_root_endpoint():
    """Verify GET / returns application information and 200 OK."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["app"] == settings.APP_NAME
    assert data["status"] == "online"
    assert data["docs_url"] == "/docs"
    assert data["ui_url"] == "/ui"


def test_frontend_ui_served():
    """Verify frontend HTML, CSS, and JS are properly served by FastAPI."""
    # Test convenience redirect
    res_dash = client.get("/dashboard", follow_redirects=False)
    assert res_dash.status_code in (302, 307)
    assert res_dash.headers["location"] == "/ui"

    # Test UI HTML
    res_ui = client.get("/ui/")
    assert res_ui.status_code == 200
    assert "ProgressPro" in res_ui.text
    assert "<!DOCTYPE html>" in res_ui.text

    # Test UI CSS
    res_css = client.get("/ui/css/style.css")
    assert res_css.status_code == 200
    assert "--bg-base" in res_css.text

    # Test UI JS
    res_js = client.get("/ui/js/app.js")
    assert res_js.status_code == 200
    assert "ProgressPro Main Application Controller" in res_js.text


def test_health_check():
    """Verify GET /health returns 200 OK with expected schema."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == settings.APP_NAME
    assert data["version"] == settings.APP_VERSION
    assert "database" in data


def test_password_hashing():
    """Verify bcrypt password hashing and verification."""
    password = "SuperSecretPassword123!"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("WrongPassword!", hashed) is False


def test_jwt_lifecycle():
    """Verify JWT access token creation and decoding."""
    user_id = 42
    token = create_access_token(subject=user_id)
    payload = decode_token(token)
    assert payload["sub"] == str(user_id)
    assert payload["type"] == "access"
    assert "exp" in payload
    assert "iat" in payload
