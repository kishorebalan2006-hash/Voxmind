"""
Unit Tests for Speech-to-Text Pipeline, Audio Preprocessor, and Transcript Endpoints.
"""

import os
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import meetings
from app.services.stt.fake_stt_provider import FakeSpeechToTextProvider
from app.services.audio.audio_preprocessor import AudioPreprocessor
from app.services.processing.meeting_processing_service import MeetingProcessingService
from app.core.exceptions import AppException
from tests.conftest import MockMeetingRepository


@pytest.mark.asyncio
async def test_fake_stt_provider_transcription():
    provider = FakeSpeechToTextProvider(simulated_language="en")
    assert provider.provider_name == "fake_stt"

    result = await provider.transcribe(audio_file_path="mock.m4a", language_code="en")
    assert result.language == "en"
    assert result.duration_seconds > 0
    assert len(result.segments) >= 4
    for seg in result.segments:
        assert seg.text
        assert seg.end_time_ms >= seg.start_time_ms
        assert seg.confidence is not None
        assert seg.formatted_start_time


def test_audio_preprocessor_validation(tmp_path):
    # 1. Missing file
    with pytest.raises(AppException) as exc1:
        AudioPreprocessor.validate_audio_file(str(tmp_path / "non_existent.m4a"))
    assert exc1.value.code == "AUDIO_NOT_FOUND"

    # 2. Empty file
    empty_file = tmp_path / "empty.m4a"
    empty_file.write_bytes(b"")
    with pytest.raises(AppException) as exc2:
        AudioPreprocessor.validate_audio_file(str(empty_file))
    assert exc2.value.code == "EMPTY_AUDIO_FILE"

    # 3. Unsupported format
    txt_file = tmp_path / "test.txt"
    txt_file.write_bytes(b"hello world")
    with pytest.raises(AppException) as exc3:
        AudioPreprocessor.validate_audio_file(str(txt_file))
    assert exc3.value.code == "UNSUPPORTED_AUDIO_FORMAT"

    # 4. Valid audio file
    valid_file = tmp_path / "test_recording.m4a"
    valid_file.write_bytes(b"dummy_m4a_audio_bytes_12345")
    info = AudioPreprocessor.validate_audio_file(str(valid_file))
    assert info["valid"] is True
    assert info["size"] > 0
    assert info["extension"] == ".m4a"


def test_transcript_processing_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo
    meetings.meeting_processing_service = MeetingProcessingService(meeting_repository=mock_repo)

    # 1. Process transcript trigger
    res_proc = test_client.post(
        "/api/v1/meetings/mtg_001/transcript/process",
        headers={"Authorization": "Bearer mock_token"},
        json={"recording_id": "rec_001", "language": "en"},
    )
    assert res_proc.status_code == 200
    proc_data = res_proc.json()
    assert proc_data["meetingId"] == "mtg_001"
    assert proc_data["jobId"]

    # 2. Check transcript status
    res_status = test_client.get(
        "/api/v1/meetings/mtg_001/transcript/status",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["meetingId"] == "mtg_001"

    # 3. Retrieve meeting transcript
    res_transcript = test_client.get(
        "/api/v1/meetings/mtg_001/transcript",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_transcript.status_code == 200
    transcript_data = res_transcript.json()
    assert transcript_data["meetingId"] == "mtg_001"
    assert "segments" in transcript_data

    app.dependency_overrides.clear()


def test_transcript_cross_tenant_isolation(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo
    meetings.meeting_processing_service = MeetingProcessingService(meeting_repository=mock_repo)

    # User in org_alpha tries to access mtg_002 (owned by org_beta) -> Expect 404
    res = test_client.get(
        "/api/v1/meetings/mtg_002/transcript",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res.status_code == 404

    app.dependency_overrides.clear()
