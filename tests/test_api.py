"""
FastAPI Integration Tests for AI Customer Support Decision Engine API.
"""

import pytest
from fastapi.testclient import TestClient
from backend.main import app


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_01_health_endpoint(client):
    """GET /health should return 200 OK and status ok."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_02_status_endpoint(client):
    """GET /api/status should return ready with loaded models and index size."""
    response = client.get("/api/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["classifier_loaded"] is True
    assert data["retrieval_index_size"] > 0
    assert "thresholds" in data


def test_03_empty_message_validation(client):
    """POST /api/support with empty message should return 422 Unprocessable Entity."""
    response = client.post("/api/support", json={"message": ""})
    assert response.status_code == 422


def test_04_whitespace_message_validation(client):
    """POST /api/support with whitespace only should return 422."""
    response = client.post("/api/support", json={"message": "   "})
    assert response.status_code == 422


def test_05_account_deletion_escalation(client):
    """POST /api/support with 'delete my account' should return ESCALATE."""
    response = client.post("/api/support", json={"message": "delete my account please"})
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ESCALATE"
    assert data["escalation_reason"] is not None
    assert len(data["draft_reply"]) == 0
    assert "trust_checks" in data
    # At least one trust check should have failed
    assert any(c["passed"] is False for c in data["trust_checks"])


def test_06_financial_refund_escalation(client):
    """POST /api/support with refund demand should return ESCALATE."""
    response = client.post("/api/support", json={"message": "give me a refund for my order right now"})
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ESCALATE"
    assert data["escalation_reason"] is not None


def test_07_ambiguous_short_query_escalation(client):
    """POST /api/support with ambiguous query 'help' should return ESCALATE."""
    response = client.post("/api/support", json={"message": "help"})
    assert response.status_code == 200
    data = response.json()
    assert data["decision"] == "ESCALATE"
    assert data["escalation_reason"] is not None


def test_08_supported_query_auto_handle(client):
    """POST /api/support with valid supported query returns proper structure and trust checks."""
    response = client.post(
        "/api/support",
        json={"message": "Where is my package? The tracking number has not updated."}
    )
    assert response.status_code == 200
    data = response.json()
    assert "decision" in data
    assert data["decision"] in ["AUTO-HANDLE", "ESCALATE"]
    assert "intent" in data
    assert "intent_confidence" in data
    assert "retrieved_cases" in data
    assert isinstance(data["retrieved_cases"], list)
    assert len(data["retrieved_cases"]) > 0
    assert "evidence" in data
    assert "trust_checks" in data
    assert len(data["trust_checks"]) == 6
