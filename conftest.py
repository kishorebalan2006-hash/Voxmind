"""
Pytest Test Fixtures and Mocks for VoxMind FastAPI Backend.
"""

import pytest
from typing import Dict, Any, Optional
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.models.auth_user import AuthenticatedUser, UserRole
from app.repositories.meeting_repository import MeetingRepository
from app.repositories.user_repository import UserRepository
from app.repositories.organization_repository import OrganizationRepository


class MockMeetingRepository(MeetingRepository):
    def __init__(self):
        super().__init__(db=None)
        self.meetings: Dict[str, Dict[str, Any]] = {
            "mtg_001": {
                "id": "mtg_001",
                "organizationId": "org_alpha",
                "title": "Alpha Sprint Planning",
                "status": "scheduled",
                "createdById": "usr_alpha_1",
                "createdAt": "2026-08-28T10:00:00Z",
            },
            "mtg_002": {
                "id": "mtg_002",
                "organizationId": "org_beta",
                "title": "Beta Secret Strategy",
                "status": "recording",
                "createdById": "usr_beta_1",
                "createdAt": "2026-08-28T11:00:00Z",
            },
        }

    async def get_meeting(self, organization_id: str, meeting_id: str) -> Optional[Dict[str, Any]]:
        m = self.meetings.get(meeting_id)
        if m and m.get("organizationId") == organization_id:
            return m
        return None

    async def list_meetings(self, organization_id: str, limit: int = 20, cursor: Optional[str] = None):
        items = [m for m in self.meetings.values() if m.get("organizationId") == organization_id]
        return items, None, len(items)

    async def update_meeting_status(self, organization_id: str, meeting_id: str, status: str, extra_fields=None):
        m = self.meetings.get(meeting_id)
        if m and m.get("organizationId") == organization_id:
            m["status"] = status
            if extra_fields:
                m.update(extra_fields)
            return True
        return False


@pytest.fixture
def test_client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def mock_user_alpha() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id="usr_alpha_1",
        email="alice@alpha.corp",
        display_name="Alice Alpha",
        organization_id="org_alpha",
        role=UserRole.ADMIN,
    )


@pytest.fixture
def mock_user_beta() -> AuthenticatedUser:
    return AuthenticatedUser(
        user_id="usr_beta_1",
        email="bob@beta.corp",
        display_name="Bob Beta",
        organization_id="org_beta",
        role=UserRole.MEMBER,
    )
