# ==============================================================================
# AI Agent Webhook Middleware - Elite Enterprise Test Suite
# ==============================================================================

import hmac
import hashlib
import json
import pytest
from fastapi.testclient import TestClient
from main import app, settings

client = TestClient(app)

def generate_test_signature(body: bytes, secret: str) -> str:
    """Helper utility to generate a cryptographically valid HMAC-SHA256 signature."""
    signature = hmac.new(
        secret.encode("utf-8"),
        msg=body,
        digestmod=hashlib.sha256
    ).hexdigest()
    return f"sha256={signature}"


def test_health_check():
    """Verify that the health check endpoint returns active status and proper environment metadata."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "AI Agent Webhook Middleware"
    assert "timestamp" in data


def test_webhook_ingest_success():
    """Verify successful webhook ingestion with a valid payload and correct HMAC signature."""
    payload = {
        "event_type": "lead.extracted",
        "source": "apify-scraper",
        "payload": {
            "company_name": "Acme Corp",
            "contact_email": "founder@acmecorp.com",
            "status": "qualified"
        }
    }
    body_bytes = json.dumps(payload).encode("utf-8")
    signature = generate_test_signature(body_bytes, settings.webhook_secret)

    response = client.post(
        "/webhook/ingest",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature
        }
    )

    assert response.status_code == 202
    data = response.json()
    assert data["status"] == "success"
    assert data["event_type"] == "lead.extracted"
    assert data["source"] == "apify-scraper"


def test_webhook_unauthorized_missing_signature(monkeypatch):
    """Verify requests lacking a signature header are rejected with 401 in production."""
    monkeypatch.setattr(settings, "environment", "production")
    
    payload = {
        "event_type": "lead.extracted",
        "source": "apify-scraper",
        "payload": {"test": "data"}
    }
    
    response = client.post("/webhook/ingest", json=payload)
    assert response.status_code == 401
    assert "Invalid signature" in response.json()["detail"]


@pytest.mark.parametrize(
    "invalid_signature",
    [
        "sha256=deadbeefinvalidhashstring1234567890abcdef",
        "invalid_format_no_prefix",
        "sha256=" + "0" * 64, # Mismatched hash
        "", # Empty header string
    ]
)
def test_webhook_unauthorized_invalid_signatures(monkeypatch, invalid_signature):
    """Verify that forged, malformed, or mismatched signatures are securely blocked."""
    monkeypatch.setattr(settings, "environment", "production")
    
    payload = {
        "event_type": "lead.extracted",
        "source": "apify-scraper",
        "payload": {"test": "data"}
    }
    body_bytes = json.dumps(payload).encode("utf-8")

    response = client.post(
        "/webhook/ingest",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": invalid_signature
        }
    )
    assert response.status_code == 401
    assert "Invalid signature" in response.json()["detail"]


@pytest.mark.parametrize(
    "malformed_payload",
    [
        {}, # Completely empty object
        {"event_type": "lead.extracted"}, # Missing source and payload
        {"source": "apify-scraper", "payload": {}}, # Missing event_type
        {"event_type": 12345, "source": "apify-scraper", "payload": {}}, # Wrong data type for event_type
    ]
)
def test_webhook_malformed_payload_validation(malformed_payload):
    """Verify Pydantic v2 schema validation catches malformed or invalid structures instantly."""
    body_bytes = json.dumps(malformed_payload).encode("utf-8")
    signature = generate_test_signature(body_bytes, settings.webhook_secret)

    response = client.post(
        "/webhook/ingest",
        content=body_bytes,
        headers={
            "Content-Type": "application/json",
            "X-Webhook-Signature": signature
        }
    )
    assert response.status_code == 400
    assert "validation failed" in response.json()["detail"]
  
