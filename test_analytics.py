"""
Unit & Integration Tests for Multi-Tenant Analytics and Aggregations.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import analytics, meetings
from app.services.analytics.analytics_service import AnalyticsService
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.models.intelligence import ActionItemEntity, DecisionEntity, QuestionEntity
from app.models.transcript import TranscriptSegmentEntity
from tests.conftest import MockMeetingRepository


@pytest.mark.asyncio
async def test_analytics_service_empty_organization_safe_zero_division():
    service = AnalyticsService(
        meeting_repo=MockMeetingRepository(),
        intelligence_repo=IntelligenceRepository(),
        transcript_repo=TranscriptRepository(),
    )

    res = await service.get_full_analytics("org_empty", days=30)
    assert res.overview.totalMeetings == 0
    assert res.overview.totalMeetingHours == 0.0
    assert res.overview.averageMeetingDurationMinutes == 0.0
    assert res.overview.actionItemStats.completionRate == 0.0
    assert res.overview.decisionStats.decisionsPerMeeting == 0.0


@pytest.mark.asyncio
async def test_analytics_service_aggregates_action_items_and_decisions():
    intel_repo = IntelligenceRepository()
    transcript_repo = TranscriptRepository()
    meeting_repo = MockMeetingRepository()

    # Seed data
    await intel_repo.save_action_items(
        "org_alpha",
        "mtg_001",
        [
            ActionItemEntity(
                id="act_01",
                meetingId="mtg_001",
                title="Complete STT Load Testing",
                assigneeName="Alex",
                dueDate="2026-08-30",
                status="done",
            ),
            ActionItemEntity(
                id="act_02",
                meetingId="mtg_001",
                title="Update Firebase Security Rules",
                assigneeName="Sarah",
                dueDate="2026-08-01",  # Overdue
                status="pending",
            ),
        ],
    )

    await intel_repo.save_decisions(
        "org_alpha",
        "mtg_001",
        [
            DecisionEntity(
                id="dec_01",
                meetingId="mtg_001",
                title="Adopt WebSocket Streaming",
                description="Chosen for sub-500ms latency.",
                decisionMaker="Sarah Mitchell",
            )
        ],
    )

    await transcript_repo.save_segments(
        "org_alpha",
        "mtg_001",
        [
            TranscriptSegmentEntity(
                id="seg_01",
                speaker_id="spk_01",
                speaker_name="Sarah Mitchell",
                start_time_ms=0,
                end_time_ms=60000,
                text="Hello world",
                timestamp="00:00",
            ),
            TranscriptSegmentEntity(
                id="seg_02",
                speaker_id="spk_02",
                speaker_name="Alex Rivera",
                start_time_ms=60000,
                end_time_ms=120000,
                text="Hello team",
                timestamp="01:00",
            ),
        ],
    )

    service = AnalyticsService(
        meeting_repo=meeting_repo,
        intelligence_repo=intel_repo,
        transcript_repo=transcript_repo,
    )

    res = await service.get_full_analytics("org_alpha", days=30)
    assert res.overview.totalMeetings == 2
    assert res.overview.actionItemStats.totalActions == 2
    assert res.overview.actionItemStats.completed == 1
    assert res.overview.actionItemStats.overdue == 1
    assert res.overview.actionItemStats.completionRate == 50.0
    assert res.overview.decisionStats.totalDecisions == 1
    assert len(res.speakerAnalytics) == 2
    assert len(res.upcomingDeadlines) == 2


def test_analytics_api_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo
    analytics._analytics_service = AnalyticsService(
        meeting_repo=mock_repo,
        intelligence_repo=IntelligenceRepository(),
        transcript_repo=TranscriptRepository(),
    )

    # 1. Full analytics
    res_full = test_client.get(
        "/api/v1/analytics/full?days=30",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_full.status_code == 200
    data = res_full.json()
    assert "overview" in data
    assert "meetingTrends" in data

    # 2. Overview
    res_ov = test_client.get(
        "/api/v1/analytics/overview",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_ov.status_code == 200

    # 3. Trends
    res_tr = test_client.get(
        "/api/v1/analytics/trends",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_tr.status_code == 200

    # 4. Speakers
    res_spk = test_client.get(
        "/api/v1/analytics/speakers",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_spk.status_code == 200

    app.dependency_overrides.clear()
