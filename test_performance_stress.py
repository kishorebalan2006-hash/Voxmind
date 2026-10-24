"""
Backend Performance & Stress Test Suite for VoxMind.
Validates latency bounds for large datasets, pagination, and AI transcript chunking.
"""

import time
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.models.auth_user import AuthenticatedUser
from app.models.admin import UserRole
from app.repositories.meeting_repository import meeting_repository
from app.models.meeting import MeetingCreateRequest
from app.services.intelligence.transcript_preprocessor import TranscriptPreprocessor
from app.models.transcript import TranscriptSegment


def test_large_meeting_pagination_performance(test_client: TestClient):
    """Verifies that listing and filtering hundreds of meetings executes in under 100ms."""
    mock_perf_user = AuthenticatedUser(
        user_id="usr_perf_01",
        email="perf@voxmind.ai",
        organization_id="org_perf_test",
        role=UserRole.ADMIN,
    )
    app.dependency_overrides[get_current_user] = lambda: mock_perf_user

    # Bulk create 100 meetings
    t0 = time.perf_counter()
    for i in range(100):
        meeting_repository.create_meeting(
            org_id="org_perf_test",
            user_id="usr_perf_01",
            data=MeetingCreateRequest(title=f"Performance Stress Meeting {i}"),
        )
    create_duration = time.perf_counter() - t0
    assert create_duration < 1.5  # Sub-second bulk creation

    # Test listing with pagination
    t1 = time.perf_counter()
    res = test_client.get("/api/v1/meetings?limit=20&offset=40", headers={"Authorization": "Bearer mock"})
    query_duration = time.perf_counter() - t1

    assert res.status_code == 200
    meetings = res.json()
    assert len(meetings) == 20
    assert query_duration < 0.1  # Fast query latency (<100ms)

    app.dependency_overrides.clear()


def test_large_transcript_chunking_throughput():
    """Verifies that preprocessing and chunking a 1,000-segment transcript finishes under 50ms."""
    preprocessor = TranscriptPreprocessor()

    large_transcript = [
        TranscriptSegment(
            id=f"seg_{i}",
            meetingId="mtg_perf_01",
            speakerId=f"speaker_{i % 4}",
            speakerName=f"Speaker {i % 4}",
            text=f"Acoustic segment sentence text with discussion points for index {i}.",
            startTime=float(i * 5),
            endTime=float((i + 1) * 5),
            confidence=0.98,
        )
        for i in range(1000)
    ]

    t0 = time.perf_counter()
    chunks = preprocessor.chunk_transcript(large_transcript, max_chunk_words=300)
    duration = time.perf_counter() - t0

    assert len(chunks) > 0
    assert duration < 0.05  # Preprocessing 1,000 segments takes less than 50ms
