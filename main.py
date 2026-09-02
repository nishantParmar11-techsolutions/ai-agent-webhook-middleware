# ==============================================================================
# AI Agent Webhook Middleware - Enterprise Hardened FastAPI Service
# ==============================================================================

import hmac
import hashlib
import logging
from datetime import datetime
from typing import Any, Dict, Optional
from fastapi import FastAPI, Header, HTTPException, Request, status
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

# 1. Configure Enterprise Structured Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("webhook-middleware")

# 2. Type-Safe Environment Configuration
class Settings(BaseSettings):
    webhook_secret: str = "default-change-me-in-production"
    environment: str = "production"

    model_config = {"env_file": ".env", "extra": "ignore"}

settings = Settings()

app = FastAPI(
    title="AI Agent Webhook Middleware",
    description="Enterprise-grade asynchronous webhook routing, validation, and security layer.",
    version="2.0.0"
)

# 3. Strict Input Validation Schema
class WebhookPayload(BaseModel):
    event_type: str = Field(..., description="Type of event (e.g., lead.extracted)")
    source: str = Field(..., description="Source system identifier (e.g., apify-scraper)")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] = Field(..., description="Structured data payload")


def verify_signature(payload_body: bytes, signature_header: Optional[str]) -> bool:
    """
    Cryptographically verifies the HMAC-SHA256 webhook signature 
    to ensure payload authenticity and prevent spoofing attacks.
    """
    if not signature_header:
        return False
    
    # Compute expected signature using our shared secret
    expected_signature = hmac.new(
        settings.webhook_secret.encode("utf-8"),
        msg=payload_body,
        digestmod=hashlib.sha256
    ).hexdigest()

    # Constant-time comparison to prevent timing attacks
    return hmac.compare_digest(f"sha256={expected_signature}", signature_header)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    """Health check endpoint for container orchestration and uptime monitoring."""
    return {
        "status": "healthy",
        "service": "ai-agent-webhook-middleware",
        "environment": settings.environment,
        "timestamp": datetime.utcnow().isoformat()
    }


@app.post("/webhook/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_webhook(
    request: Request,
    x_webhook_signature: Optional[str] = Header(None, alias="X-Webhook-Signature")
):
    """
    Ingests, cryptographically verifies, validates via Pydantic, and handles 
    incoming webhook payloads securely.
    """
    # Read raw body for cryptographic verification
    body_bytes = await request.body()

    # Verify signature security check
    if settings.environment == "production" and not verify_signature(body_bytes, x_webhook_signature):
        logger.warning("Security alert: Invalid or missing webhook signature detected.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid signature. Webhook authentication failed."
        )

    try:
        # Parse and validate JSON against Pydantic schema
        json_data = await request.json()
        incoming = WebhookPayload(**json_data)

        # Structured enterprise logging
        logger.info(
            f"Successfully processed event '{incoming.event_type}' "
            f"from source '{incoming.source}' at timestamp {incoming.timestamp}"
        )
        
        return {
            "status": "success",
            "message": "Payload cryptographically verified, validated, and accepted.",
            "event_type": incoming.event_type,
            "source": incoming.source,
            "processed_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Payload validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Webhook payload validation failed: {str(e)}"
)
      
