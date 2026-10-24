"""
Tests for Push/In-app Notifications & Calendar Integration.
"""

import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import notifications
from app.models.notification import (
    NotificationItem,
    NotificationType,
    NotificationPreferences,
    CalendarEventRequest,
)
from app.repositories.notification_repository import NotificationRepository
from app.services.notifications.notification_service import NotificationService
from app.services.calendar.calendar_service import UniversalCalendarProvider


@pytest.mark.asyncio
async def test_notification_service_and_deduplication():
    repo = NotificationRepository()
    service = NotificationService(repo=repo)

    # 1. Trigger processing completed
    notif1 = await service.trigger_processing_completed(
        org_id="org_alpha",
        user_id="user_alpha_01",
        meeting_id="mtg_001",
        meeting_title="Sprint Architecture",
    )
    assert notif1 is not None
    assert notif1.type == NotificationType.processingCompleted
    assert notif1.isRead is False

    # 2. Duplicate trigger with same dedup_key returns existing without creating extra entry
    notif2 = await service.trigger_processing_completed(
        org_id="org_alpha",
        user_id="user_alpha_01",
        meeting_id="mtg_001",
        meeting_title="Sprint Architecture",
    )
    assert notif2.id == notif1.id

    notifs = await repo.get_user_notifications("org_alpha", "user_alpha_01")
    assert len(notifs) == 1

    # 3. Mark as read
    res = await repo.mark_as_read("org_alpha", "user_alpha_01", notif1.id)
    assert res is True

    unread = await repo.get_user_notifications("org_alpha", "user_alpha_01", unread_only=True)
    assert len(unread) == 0


@pytest.mark.asyncio
async def test_calendar_service_generates_valid_ical():
    provider = UniversalCalendarProvider()
    req = CalendarEventRequest(
        meetingId="mtg_test",
        title="VoxMind Product Review",
        startTime=datetime(2026, 8, 30, 14, 0, 0),
        endTime=datetime(2026, 8, 30, 15, 0, 0),
    )

    res = await provider.create_event(req)
    assert res.meetingId == "mtg_test"
    assert "BEGIN:VCALENDAR" in res.icsContent
    assert "SUMMARY:VoxMind Product Review" in res.icsContent
    assert "https://calendar.google.com" in res.googleCalendarUrl


def test_notification_endpoints(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    repo = NotificationRepository()
    notifications._repo = repo
    notifications._service = NotificationService(repo=repo)

    # 1. Initial list empty
    res = test_client.get("/api/v1/notifications", headers={"Authorization": "Bearer mock"})
    assert res.status_code == 200
    assert res.json() == []

    # 2. Preferences
    res_pref = test_client.get("/api/v1/notifications/preferences", headers={"Authorization": "Bearer mock"})
    assert res_pref.status_code == 200
    assert res_pref.json()["meetingReminders"] is True

    # 3. Calendar event create
    res_cal = test_client.post(
        "/api/v1/calendar/events",
        json={
            "meetingId": "mtg_001",
            "title": "Strategy Sync",
            "startTime": "2026-08-30T10:00:00Z",
            "endTime": "2026-08-30T10:45:00Z",
        },
        headers={"Authorization": "Bearer mock"},
    )
    assert res_cal.status_code == 200
    assert "icsContent" in res_cal.json()

    app.dependency_overrides.clear()
