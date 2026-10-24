"""
Unit & Integration Tests for SaaS Plans, Entitlements, Metering, and Quotas.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.repositories.plan_repository import plan_repository
from app.services.usage.metering_service import usage_metering_service
from app.services.usage.entitlement_service import entitlement_service
from app.models.plan import PlanTier, UsageEventType


def test_plans_and_entitlements(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha

    # 1. List all plans
    res = test_client.get("/api/v1/plans", headers={"Authorization": "Bearer mock"})
    assert res.status_code == 200
    plans = res.json()
    assert len(plans) == 4
    tiers = [p["tier"] for p in plans]
    assert "free" in tiers
    assert "enterprise" in tiers

    # 2. Get org plan (default Free)
    res_org = test_client.get("/api/v1/plans/organization", headers={"Authorization": "Bearer mock"})
    assert res_org.status_code == 200
    org_plan = res_org.json()
    assert org_plan["tier"] == "free"
    assert org_plan["entitlements"]["maxUsers"] == 5

    app.dependency_overrides.clear()


def test_metered_usage_and_idempotency(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    org_id = mock_user_alpha.organization_id

    # Record 10 meeting minutes
    recorded1 = usage_metering_service.record_usage(
        org_id=org_id,
        user_id=mock_user_alpha.user_id,
        event_type=UsageEventType.meetingMinutes,
        quantity=10.0,
        reference_id="ref_mtg_01",
    )
    assert recorded1 is True

    # Retrying same reference ID must return False (deduplicated)
    recorded2 = usage_metering_service.record_usage(
        org_id=org_id,
        user_id=mock_user_alpha.user_id,
        event_type=UsageEventType.meetingMinutes,
        quantity=10.0,
        reference_id="ref_mtg_01",
    )
    assert recorded2 is False

    # Check usage API
    res_usage = test_client.get("/api/v1/usage", headers={"Authorization": "Bearer mock"})
    assert res_usage.status_code == 200
    usage_data = res_usage.json()
    assert usage_data["meetingMinutes"] >= 10.0

    # Check usage summary & limit checks
    res_summary = test_client.get("/api/v1/usage/summary", headers={"Authorization": "Bearer mock"})
    assert res_summary.status_code == 200
    summary = res_summary.json()
    assert summary["planTier"] == "free"
    assert len(summary["metrics"]) >= 7

    app.dependency_overrides.clear()


def test_entitlement_limit_enforcement():
    org_id = "org_test_limit"
    plan_repository.set_organization_plan(org_id, PlanTier.free)

    # Free plan maxReportsPerMonth is 20
    # Check limit before
    allowed1, err1 = entitlement_service.check_limit(org_id, "Generated Reports", 5)
    assert allowed1 is True
    assert err1 is None

    # Artificially consume 20 reports
    usage = plan_repository.get_organization_usage(org_id)
    usage.reportsGenerated = 20

    # Exceed limit
    allowed2, err2 = entitlement_service.check_limit(org_id, "Generated Reports", 1)
    assert allowed2 is False
    assert "LIMIT_REACHED" in (err2 or "")

    # Upgrade to Enterprise (unlimited)
    plan_repository.set_organization_plan(org_id, PlanTier.enterprise)
    allowed3, err3 = entitlement_service.check_limit(org_id, "Generated Reports", 500)
    assert allowed3 is True
    assert err3 is None
