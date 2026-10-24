"""
Unit & Integration Tests for Meeting Reports & Document Export.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import reports
from app.models.report import (
    ReportType,
    ReportFormat,
    ReportGenerationRequest,
)
from app.repositories.report_repository import ReportRepository
from app.repositories.intelligence_repository import IntelligenceRepository
from app.repositories.transcript_repository import TranscriptRepository
from app.services.reports.report_generator import ReportGenerationService
from tests.conftest import MockMeetingRepository


@pytest.mark.asyncio
async def test_report_generation_service_all_types():
    meeting_repo = MockMeetingRepository()
    intel_repo = IntelligenceRepository()
    transcript_repo = TranscriptRepository()
    report_repo = ReportRepository()

    service = ReportGenerationService(
        meeting_repo=meeting_repo,
        intel_repo=intel_repo,
        transcript_repo=transcript_repo,
        report_repo=report_repo,
    )

    # 1. Executive Report
    rep_exec = await service.generate_report(
        org_id="org_alpha",
        user_id="user_alpha_01",
        meeting_id="mtg_001",
        request=ReportGenerationRequest(reportType=ReportType.executive),
    )
    assert rep_exec.reportType == ReportType.executive
    assert "VOXMIND ENTERPRISE REPORT: EXECUTIVE" in rep_exec.fileContent
    assert rep_exec.reportVersion == 1

    # 2. Re-generating increments version
    rep_exec_v2 = await service.generate_report(
        org_id="org_alpha",
        user_id="user_alpha_01",
        meeting_id="mtg_001",
        request=ReportGenerationRequest(reportType=ReportType.executive),
    )
    assert rep_exec_v2.reportVersion == 2

    # 3. Action Items Report
    rep_acts = await service.generate_report(
        org_id="org_alpha",
        user_id="user_alpha_01",
        meeting_id="mtg_001",
        request=ReportGenerationRequest(reportType=ReportType.actionItems),
    )
    assert rep_acts.reportType == ReportType.actionItems


def test_reports_api_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    report_repo = ReportRepository()
    reports._report_repo = report_repo
    reports._report_service = ReportGenerationService(
        meeting_repo=MockMeetingRepository(),
        intel_repo=IntelligenceRepository(),
        transcript_repo=TranscriptRepository(),
        report_repo=report_repo,
    )

    # 1. Generate Report
    res_gen = test_client.post(
        "/api/v1/meetings/mtg_001/reports",
        json={"reportType": "executive", "format": "pdf"},
        headers={"Authorization": "Bearer mock"},
    )
    assert res_gen.status_code == 200
    data = res_gen.json()
    report_id = data["report"]["id"]
    assert report_id.startswith("rep_")

    # 2. List Meeting Reports
    res_list = test_client.get(
        "/api/v1/meetings/mtg_001/reports",
        headers={"Authorization": "Bearer mock"},
    )
    assert res_list.status_code == 200
    assert len(res_list.json()) == 1

    # 3. Download Report
    res_dl = test_client.get(
        f"/api/v1/meetings/mtg_001/reports/{report_id}/download",
        headers={"Authorization": "Bearer mock"},
    )
    assert res_dl.status_code == 200
    assert b"VOXMIND" in res_dl.content

    app.dependency_overrides.clear()
