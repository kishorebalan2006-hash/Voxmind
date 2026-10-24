"""
Unit Tests for Speaker Diarization, Transcript Alignment Merger, and Speaker Management Endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import meetings
from app.services.diarization.fake_diarization_provider import FakeSpeakerDiarizationProvider
from app.services.diarization.diarization_merger import TranscriptSpeakerMerger
from app.services.stt.fake_stt_provider import FakeSpeechToTextProvider
from app.models.transcript import TranscriptSegment
from app.models.speaker import SpeakerSegment, SpeakerMappingStatus
from tests.conftest import MockMeetingRepository


def test_transcript_speaker_merger_alignment():
    # 1. Clear overlap alignment
    transcript_segments = [
        TranscriptSegment(
            id="seg_01",
            text="First speaker segment",
            start_time_ms=1000,
            end_time_ms=5000,
        ),
        TranscriptSegment(
            id="seg_02",
            text="Second speaker segment",
            start_time_ms=6000,
            end_time_ms=10000,
        ),
        TranscriptSegment(
            id="seg_03",
            text="Ambiguous segment without overlap",
            start_time_ms=20000,
            end_time_ms=25000,
        ),
    ]

    speaker_turns = [
        SpeakerSegment(
            id="turn_01",
            speaker_id="speaker_0",
            start_time_ms=800,
            end_time_ms=5200,
            confidence=0.98,
        ),
        SpeakerSegment(
            id="turn_02",
            speaker_id="speaker_1",
            start_time_ms=5800,
            end_time_ms=10200,
            confidence=0.95,
        ),
    ]

    participant_candidates = [
        {"id": "usr_sarah", "displayName": "Sarah Connor"},
        {"id": "usr_david", "displayName": "David Miller"},
    ]

    merged_segments, speakers = TranscriptSpeakerMerger.merge(
        transcript_segments=transcript_segments,
        speaker_turns=speaker_turns,
        organization_id="org_alpha",
        meeting_id="mtg_001",
        participant_candidates=participant_candidates,
    )

    # Verify seg_01 is mapped to Sarah Connor
    assert merged_segments[0].speaker_id == "speaker_0"
    assert merged_segments[0].speaker_name == "Sarah Connor"

    # Verify seg_02 is mapped to David Miller
    assert merged_segments[1].speaker_id == "speaker_1"
    assert merged_segments[1].speaker_name == "David Miller"

    # Verify seg_03 is assigned to 'unknown' / 'Unknown Speaker'
    assert merged_segments[2].speaker_id == "unknown"
    assert merged_segments[2].speaker_name == "Unknown Speaker"

    # Verify speakers accumulated statistics
    assert len(speakers) == 3
    unknown_spk = next(s for s in speakers if s.id == "unknown")
    assert unknown_spk.display_name == "Unknown Speaker"


def test_speaker_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo

    # 1. Process speakers trigger
    proc_res = test_client.post(
        "/api/v1/meetings/mtg_001/speakers/process",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert proc_res.status_code == 200
    assert proc_res.json()["meetingId"] == "mtg_001"

    # 2. Get speaker processing status
    status_res = test_client.get(
        "/api/v1/meetings/mtg_001/speakers/status",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["meetingId"] == "mtg_001"

    # 3. List speakers for meeting
    res = test_client.get(
        "/api/v1/meetings/mtg_001/speakers",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) >= 2
    speaker_id = data["items"][0]["id"]

    # 4. Update speaker display name
    patch_res = test_client.patch(
        f"/api/v1/meetings/mtg_001/speakers/{speaker_id}",
        headers={"Authorization": "Bearer mock_token"},
        json={"display_name": "Dr. Sarah Mitchell", "color_hex": "#059669"},
    )
    assert patch_res.status_code == 200
    updated_speaker = patch_res.json()
    assert updated_speaker["displayName"] == "Dr. Sarah Mitchell"
    assert updated_speaker["colorHex"] == "#059669"

    app.dependency_overrides.clear()
