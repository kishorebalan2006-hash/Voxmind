"""
Unit & Integration Tests for Offline Data Synchronization and Idempotency.
"""

from fastapi.testclient import TestClient
from app.main import app
from app.api.dependencies.auth import get_current_user
from app.api.routes import sync


def test_sync_batch_idempotency(test_client: TestClient, mock_user_alpha):
    app.dependency_overrides[get_current_user] = lambda: mock_user_alpha
    sync._processed_idempotency_keys.clear()

    batch_payload = {
        "items": [
            {
                "id": "sync_01",
                "idempotencyKey": "idem_mtg_create_001",
                "entityType": "meeting",
                "entityId": "mtg_offline_01",
                "operation": "create",
                "payload": {"title": "Offline Created Meeting"},
            },
            {
                "id": "sync_02",
                "idempotencyKey": "idem_act_update_002",
                "entityType": "actionItem",
                "entityId": "act_002",
                "operation": "update",
                "payload": {"status": "completed"},
            },
        ]
    }

    # 1. Initial Sync Batch
    res1 = test_client.post("/api/v1/sync", json=batch_payload, headers={"Authorization": "Bearer mock"})
    assert res1.status_code == 200
    data1 = res1.json()
    assert data1["processedCount"] == 2
    assert data1["successCount"] == 2
    assert data1["results"][0]["status"] == "synced"
    assert data1["results"][1]["status"] == "synced"

    # 2. Retrying the exact same batch should return idempotent duplicate responses without errors
    res2 = test_client.post("/api/v1/sync", json=batch_payload, headers={"Authorization": "Bearer mock"})
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["processedCount"] == 2
    assert data2["successCount"] == 2
    assert data2["results"][0]["status"] == "duplicate"
    assert data2["results"][1]["status"] == "duplicate"

    # 3. Status check
    res_status = test_client.get("/api/v1/sync/status", headers={"Authorization": "Bearer mock"})
    assert res_status.status_code == 200
    assert res_status.json()["status"] == "healthy"

    app.dependency_overrides.clear()
