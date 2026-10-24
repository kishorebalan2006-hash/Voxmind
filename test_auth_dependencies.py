"""
Unit Tests for Authentication and Authorization Dependencies.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.models.auth_user import AuthenticatedUser, UserRole


def test_missing_auth_header_returns_401(test_client: TestClient):
    response = test_client.get("/api/v1/meetings")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "AUTHORIZATION_HEADER_MISSING"
    assert "requestId" in data["error"]


def test_invalid_scheme_returns_401(test_client: TestClient):
    response = test_client.get("/api/v1/meetings", headers={"Authorization": "Basic 12345"})
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "INVALID_AUTH_SCHEME"
