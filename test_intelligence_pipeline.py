"""
Unit Tests for AI Meeting Intelligence Engine, Transcript Chunking, and REST Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import intelligence, meetings
from app.models.transcript import TranscriptSegment
from app.services.intelligence.transcript_chunker import TranscriptChunker
from app.services.intelligence.fake_intelligence_provider import FakeMeetingIntelligenceProvider
from app.repositories.intelligence_repository import IntelligenceRepository
from tests.conftest import MockMeetingRepository


def test_transcript_chunker_preserves_order_and_ids():
    chunker = TranscriptChunker(max_tokens_per_chunk=50, overlap_segments=1)
    segments = [
        TranscriptSegment(id=f"seg_00{i}", meeting_id="mtg_001", text=f"This is sentence {i} in the discussion.", start_time_ms=i * 10000, end_time_ms=(i + 1) * 10000)
        for i in range(10)
    ]

    chunks = chunker.chunk_transcript(segments)
    assert len(chunks) >= 2
    assert "seg_000" in chunks[0].segment_ids
    assert "seg_009" in chunks[-1].segment_ids


@pytest.mark.asyncio
async def test_fake_intelligence_provider_extracts_structured_data():
    provider = FakeMeetingIntelligenceProvider()
    segments = [
        TranscriptSegment(id="seg_001", meeting_id="mtg_001", text="We must finalize live captioning by Friday.", speaker_name="Sarah", start_time_ms=0, end_time_ms=5000),
        TranscriptSegment(id="seg_002", meeting_id="mtg_001", text="I agree. Let's adopt WebSocket transport.", speaker_name="Alex", start_time_ms=5000, end_time_ms=10000),
    ]

    result = await provider.analyze_transcript("mtg_001", "org_alpha", segments)

    assert result.meetingId == "mtg_001"
    assert result.summary.text
    assert len(result.keyPoints) >= 2
    assert len(result.topics) >= 2
    assert len(result.decisions) >= 1
    assert len(result.actionItems) >= 2
    assert len(result.deadlines) >= 1
    assert len(result.risks) >= 1
    assert len(result.questions) >= 1

    # Check source traceability
    assert result.decisions[0].sourceSegmentIds == ["seg_001"]
    assert result.actionItems[0].sourceSegmentIds == ["seg_001"]


def test_meeting_intelligence_rest_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo
    intelligence._meeting_repo = mock_repo
    intelligence._intelligence_repo = IntelligenceRepository()
    intelligence._intelligence_provider = FakeMeetingIntelligenceProvider()

    # 1. Process intelligence
    res_proc = test_client.post(
        "/api/v1/meetings/mtg_001/intelligence/process",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_proc.status_code == 200
    data = res_proc.json()
    assert data["meetingId"] == "mtg_001"
    assert "summary" in data

    # 2. Get summary
    res_sum = test_client.get(
        "/api/v1/meetings/mtg_001/summary",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_sum.status_code == 200
    assert "text" in res_sum.json()

    # 3. Get key points
    res_kp = test_client.get(
        "/api/v1/meetings/mtg_001/key-points",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_kp.status_code == 200
    assert len(res_kp.json()) >= 1

    # 4. Get decisions
    res_dec = test_client.get(
        "/api/v1/meetings/mtg_001/decisions",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_dec.status_code == 200
    assert len(res_dec.json()) >= 1

    # 5. Get and update action item
    res_act = test_client.get(
        "/api/v1/meetings/mtg_001/action-items",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_act.status_code == 200
    action_items = res_act.json()
    assert len(action_items) >= 1
    first_id = action_items[0]["id"]

    res_patch = test_client.patch(
        f"/api/v1/meetings/mtg_001/action-items/{first_id}",
        headers={"Authorization": "Bearer mock_token"},
        json={"status": "completed"},
    )
    assert res_patch.status_code == 200
    assert res_patch.json()["status"] == "completed"

    # 6. Get deadlines, risks, questions
    res_dl = test_client.get(
        "/api/v1/meetings/mtg_001/deadlines",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_dl.status_code == 200

    res_rsk = test_client.get(
        "/api/v1/meetings/mtg_001/risks",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_rsk.status_code == 200

    res_qst = test_client.get(
        "/api/v1/meetings/mtg_001/questions",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_qst.status_code == 200

    app.dependency_overrides.clear()
