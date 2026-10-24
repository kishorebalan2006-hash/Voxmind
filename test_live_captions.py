"""
Unit Tests for Real-Time Live Captions, Session Manager, and Streaming STT.
"""

import wave

import pytest
from fastapi.testclient import TestClient
from starlette.websockets import WebSocketDisconnect
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import captions, meetings
from app.models.auth_user import AuthenticatedUser, UserRole
from app.services.stt.fake_live_stt_provider import FakeLiveSpeechToTextProvider
from app.services.captions.caption_session_manager import caption_session_manager
from app.models.live_caption import CaptionSessionStatus
from app.models.transcript import TranscriptSegment, TranscriptionResult
from app.services.stt.whisper_live_stt_provider import WhisperLiveSpeechToTextProvider
from tests.conftest import MockMeetingRepository


@pytest.mark.asyncio
async def test_fake_live_stt_provider_streaming():
    provider = FakeLiveSpeechToTextProvider()
    session_id = "test_sess_001"
    await provider.start_stream(session_id=session_id, meeting_id="mtg_001")

    segments = []
    async for seg in provider.stream_captions(session_id):
        segments.append(seg)
        if len(segments) >= 4:
            break

    await provider.stop_stream(session_id)

    assert len(segments) >= 4
    # Verify partials and finals
    partials = [s for s in segments if not s.is_final]
    finals = [s for s in segments if s.is_final]
    assert len(partials) >= 1
    assert len(finals) >= 1
    assert finals[0].speaker_name in ["Dr. Sarah Mitchell", "Alex Rivera"]


def test_live_caption_rest_endpoints(
    test_client: TestClient,
    mock_user_alpha,
    monkeypatch,
):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    monkeypatch.setattr(meetings, "_meeting_repo", mock_repo)
    monkeypatch.setattr(captions, "_meeting_repo", mock_repo)
    monkeypatch.setattr(
        caption_session_manager,
        "_stt_provider",
        FakeLiveSpeechToTextProvider(),
    )

    # 1. Start live caption session
    start_res = test_client.post(
        "/api/v1/meetings/mtg_001/captions/start",
        headers={"Authorization": "Bearer mock_token"},
        json={"language_code": "en"},
    )
    assert start_res.status_code == 200
    sess_data = start_res.json()
    assert sess_data["sessionId"].startswith("cap_sess_")
    assert sess_data["status"] == "listening"
    session_id = sess_data["sessionId"]

    # 2. Get live caption status
    status_res = test_client.get(
        "/api/v1/meetings/mtg_001/captions/status",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert status_res.status_code == 200
    assert status_res.json()["sessionId"] == session_id

    # 3. Stop live caption session
    stop_res = test_client.post(
        f"/api/v1/meetings/mtg_001/captions/stop?session_id={session_id}",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert stop_res.status_code == 200
    assert stop_res.json()["status"] == "stopped"

    app.dependency_overrides.clear()


def test_live_captions_websocket(test_client: TestClient, monkeypatch):
    mock_repo = MockMeetingRepository()
    monkeypatch.setattr(captions, "_meeting_repo", mock_repo)
    monkeypatch.setattr(
        caption_session_manager,
        "_stt_provider",
        FakeLiveSpeechToTextProvider(),
    )

    async def authenticated_user(authorization: str):
        assert authorization == "Bearer mock_token"
        return AuthenticatedUser(
            user_id="usr_alpha_1",
            email="alice@alpha.corp",
            display_name="Alice Alpha",
            organization_id="org_alpha",
            role=UserRole.MEMBER,
        )

    monkeypatch.setattr(captions, "get_current_user", authenticated_user)

    with test_client.websocket_connect("/api/v1/meetings/mtg_001/captions/stream?token=mock_token") as ws:
        # Initial status
        init_data = ws.receive_json()
        assert init_data["type"] == "status"
        assert init_data["status"] == "listening"

        ws.send_bytes(b"\x00\x00" * 16000)

        # Caption event
        caption_data = ws.receive_json()
        assert caption_data["type"] in ["partial", "final"]
        assert "segment" in caption_data
        assert caption_data["segment"]["text"]


@pytest.mark.asyncio
async def test_whisper_live_provider_transcribes_audio_for_authenticated_speaker():
    class StubWhisperProvider:
        api_key = "test-key"

        async def transcribe(self, audio_file_path: str, language_code: str):
            with wave.open(audio_file_path, "rb") as audio_file:
                assert audio_file.getframerate() == 16000
                assert audio_file.getnchannels() == 1
                assert audio_file.getnframes() == 16000
            return TranscriptionResult(
                language=language_code,
                duration_seconds=1,
                segments=[
                    TranscriptSegment(
                        id="segment-1",
                        meeting_id="meeting-1",
                        text="We can hear each other.",
                        start_time_ms=0,
                        end_time_ms=1000,
                    )
                ],
                raw_text="We can hear each other.",
                provider_name="whisper_openai",
            )

    provider = WhisperLiveSpeechToTextProvider(whisper_provider=StubWhisperProvider())
    await provider.start_stream(
        "session-1",
        "meeting-1",
        speaker_id="user-1",
        speaker_name="Participant One",
    )
    await provider.send_audio_chunk("session-1", b"\x00\x00" * 16000)
    await provider.stop_stream("session-1")

    segments = [segment async for segment in provider.stream_captions("session-1")]
    assert len(segments) == 1
    assert segments[0].text == "We can hear each other."
    assert segments[0].speaker_id == "user-1"
    assert segments[0].speaker_name == "Participant One"


@pytest.mark.asyncio
async def test_whisper_live_provider_requires_configured_api_key():
    class UnconfiguredWhisperProvider:
        api_key = ""

    provider = WhisperLiveSpeechToTextProvider(
        whisper_provider=UnconfiguredWhisperProvider()
    )

    with pytest.raises(RuntimeError, match="OPENAI_API_KEY"):
        await provider.start_stream("session-2", "meeting-1")


def test_live_captions_websocket_rejects_missing_authentication(test_client: TestClient):
    with test_client.websocket_connect(
        "/api/v1/meetings/mtg_001/captions/stream"
    ) as ws:
        with pytest.raises(WebSocketDisconnect):
            ws.receive_json()
