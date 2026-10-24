"""
Unit Tests for Meetings API and Multi-Tenant Organization Boundary Isolation.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import meetings
from tests.conftest import MockMeetingRepository


def test_list_meetings_scoped_to_user_organization(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    meetings._meeting_repo = MockMeetingRepository()

    response = test_client.get("/api/v1/meetings", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) == 1
    assert data["items"][0]["id"] == "mtg_001"
    assert data["items"][0]["organization_id"] == "org_alpha"

    app.dependency_overrides.clear()


def test_get_meeting_within_organization_succeeds(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    meetings._meeting_repo = MockMeetingRepository()

    response = test_client.get("/api/v1/meetings/mtg_001", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "mtg_001"
    assert data["title"] == "Alpha Sprint Planning"

    app.dependency_overrides.clear()


def test_get_cross_organization_meeting_returns_404(test_client: TestClient, mock_user_alpha):
    # User Alpha attempts to access Meeting 002 belonging to Organization Beta
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    meetings._meeting_repo = MockMeetingRepository()

    response = test_client.get("/api/v1/meetings/mtg_002", headers={"Authorization": "Bearer mock_token"})
    assert response.status_code == 404
    data = response.json()
    assert data["error"]["code"] == "MEETING_NOT_FOUND"

    app.dependency_overrides.clear()
