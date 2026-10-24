"""
Unit & Integration Tests for Organization Admin, RBAC, and Audit Logging.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import admin
from app.models.auth_user import AuthenticatedUser, UserRole
from app.models.admin import UserRole as AdminUserRole
from app.repositories.admin_repository import AdminRepository


@pytest.mark.asyncio
async def test_admin_repository_sole_owner_protection():
    repo = AdminRepository()

    # Attempting to demote the only owner in org_alpha should raise ValueError
    with pytest.raises(ValueError, match="Cannot demote the sole organization owner"):
        await repo.change_user_role(
            org_id="org_alpha",
            actor_id="user_alpha_01",
            actor_name="Santhoosh",
            target_user_id="user_alpha_01",
            new_role=AdminUserRole.member,
        )

    # Attempting to deactivate the only owner in org_alpha should raise ValueError
    with pytest.raises(ValueError, match="Cannot deactivate the sole organization owner"):
        await repo.deactivate_user(
            org_id="org_alpha",
            actor_id="user_alpha_01",
            actor_name="Santhoosh",
            target_user_id="user_alpha_01",
        )


def test_admin_routes_owner_access(test_client: TestClient, mock_user_alpha):
    # mock_user_alpha is OWNER
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    admin._admin_repo = AdminRepository()

    # 1. Overview
    res_ov = test_client.get("/api/v1/admin/overview", headers={"Authorization": "Bearer mock"})
    assert res_ov.status_code == 200
    assert res_ov.json()["totalUsers"] == 3

    # 2. Users list
    res_users = test_client.get("/api/v1/admin/users", headers={"Authorization": "Bearer mock"})
    assert res_users.status_code == 200
    assert len(res_users.json()["users"]) == 3

    # 3. Invite user
    res_inv = test_client.post(
        "/api/v1/admin/invitations",
        json={"email": "newdev@voxmind.ai", "role": "member"},
        headers={"Authorization": "Bearer mock"},
    )
    assert res_inv.status_code == 200
    assert res_inv.json()["email"] == "newdev@voxmind.ai"

    # 4. Audit logs list
    res_audit = test_client.get("/api/v1/admin/audit-logs", headers={"Authorization": "Bearer mock"})
    assert res_audit.status_code == 200
    assert len(res_audit.json()["logs"]) >= 2  # initial + invitation

    app.dependency_overrides.clear()


def test_admin_routes_member_forbidden(test_client: TestClient):
    member_user = AuthenticatedUser(
        user_id="user_member_01",
        email="member@voxmind.ai",
        display_name="Member Only",
        organization_id="org_alpha",
        role=UserRole.MEMBER,
    )
    app.dependency_overrides[get_current_user] = lambda: member_user

    # Attempt to access /admin/overview as normal member
    res = test_client.get("/api/v1/admin/overview", headers={"Authorization": "Bearer mock"})
    assert res.status_code == 403

    app.dependency_overrides.clear()
