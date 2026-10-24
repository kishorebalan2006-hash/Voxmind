"""
Unit Tests for AI Summary, Action Items, Key Decisions, and Meeting Intelligence Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import meetings
from app.services.summary.fake_summary_provider import FakeSummaryProvider
from app.models.speaker import Speaker
from tests.conftest import MockMeetingRepository


@pytest.mark.asyncio
async def test_fake_summary_provider():
    provider = FakeSummaryProvider()
    speakers = [
        Speaker(
            id="spk_01",
            meeting_id="mtg_001",
            organization_id="org_alpha",
            label="SPEAKER_00",
            display_name="Dr. Sarah Mitchell",
        ),
        Speaker(
            id="spk_02",
            meeting_id="mtg_001",
            organization_id="org_alpha",
            label="SPEAKER_01",
            display_name="Alex Rivera",
        ),
    ]

    intel = await provider.generate_intelligence(
        meeting_id="mtg_001",
        organization_id="org_alpha",
        meeting_title="Quarterly Review",
        transcript_text="Dr. Sarah Mitchell discussed revenue milestones.",
        speakers=speakers,
    )

    assert intel.summary.overview
    assert len(intel.summary.key_points) >= 2
    assert len(intel.action_items) >= 2
    assert len(intel.decisions) >= 2


def test_summary_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo

    # 1. Generate intelligence summary
    gen_res = test_client.post(
        "/api/v1/meetings/mtg_001/summary/generate",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert gen_res.status_code == 200
    intel_data = gen_res.json()
    assert "summary" in intel_data
    assert len(intel_data["actionItems"]) >= 2
    assert len(intel_data["decisions"]) >= 2
    action_item_id = intel_data["actionItems"][0]["id"]

    # 2. Get summary
    sum_res = test_client.get(
        "/api/v1/meetings/mtg_001/summary",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert sum_res.status_code == 200
    assert sum_res.json()["meetingId"] == "mtg_001"

    # 3. List action items
    actions_res = test_client.get(
        "/api/v1/meetings/mtg_001/action-items",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert actions_res.status_code == 200
    assert len(actions_res.json()) >= 2

    # 4. Update action item (toggle complete)
    patch_res = test_client.patch(
        f"/api/v1/meetings/mtg_001/action-items/{action_item_id}",
        headers={"Authorization": "Bearer mock_token"},
        json={"status": "completed"},
    )
    assert patch_res.status_code == 200
    assert patch_res.json()["status"] == "completed"

    # 5. List decisions
    dec_res = test_client.get(
        "/api/v1/meetings/mtg_001/decisions",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert dec_res.status_code == 200
    assert len(dec_res.json()) >= 2

    app.dependency_overrides.clear()
