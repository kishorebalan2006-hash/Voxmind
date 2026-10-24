"""
Unit Tests for Health & Readiness Endpoints.
"""

from fastapi.testclient import TestClient


def test_health_liveness(test_client: TestClient):
    response = test_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "voxmind-api"
    assert data["version"] == "1.0.0"


def test_health_readiness(test_client: TestClient):
    response = test_client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "firebase_connected" in data
