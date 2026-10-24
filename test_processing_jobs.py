"""
Unit Tests for Idempotent Meeting Processing Jobs and Status Telemetry.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import meetings
from app.services.processing.meeting_processing_service import MeetingProcessingService
from tests.conftest import MockMeetingRepository


def test_create_processing_job_idempotent(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    mock_repo = MockMeetingRepository()
    meetings._meeting_repo = mock_repo
    meetings.meeting_processing_service = MeetingProcessingService(meeting_repository=mock_repo)

    # 1. First trigger creates job
    res1 = test_client.post(
        "/api/v1/meetings/mtg_001/processing",
        headers={"Authorization": "Bearer mock_token"},
        json={"recording_id": "rec_001"},
    )
    assert res1.status_code == 200
    data1 = res1.json()
    job_id_1 = data1["jobId"]
    assert data1["status"] == "queued"

    # 2. Second trigger returns the same existing job (Idempotency)
    res2 = test_client.post(
        "/api/v1/meetings/mtg_001/processing",
        headers={"Authorization": "Bearer mock_token"},
        json={"recording_id": "rec_001"},
    )
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["jobId"] == job_id_1

    # 3. Status check returns the active job
    res_status = test_client.get(
        "/api/v1/meetings/mtg_001/processing-status",
        headers={"Authorization": "Bearer mock_token"},
    )
    assert res_status.status_code == 200
    status_data = res_status.json()
    assert status_data["jobId"] == job_id_1

    app.dependency_overrides.clear()
