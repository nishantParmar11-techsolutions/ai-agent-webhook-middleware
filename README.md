# AI Agent Webhook Middleware

[![CI Pipeline](https://github.com/YOUR_USERNAME/ai-agent-webhook-middleware/actions/workflows/ci.yml/badge.svg)](https://github.com/YOUR_USERNAME/ai-agent-webhook-middleware/actions/workflows/ci.yml)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110.0-009688.svg?logo=fastapi)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A production-grade, asynchronous backend microservice built with **FastAPI** and **Pydantic v2** designed to act as the secure routing and intelligence layer for automated data pipelines and AI agent workflows.

---

## 🏛️ Architectural Purpose

In enterprise automation architectures, external scrapers (like Apify) and AI agents should never talk directly to production databases or core CRMs. 

This service intercepts incoming raw webhook payloads, enforces cryptographic verification, validates data structures against strict schemas, and routes clean data asynchronously to downstream destinations with full telemetry and error resilience.

```text
[Scrapers / AI Agents] 
          │ (HMAC-SHA256 Signed Payload)
          ▼
┌─────────────────────────────────────────┐
│        AI Agent Webhook Middleware      │
│  ┌───────────────┐   ┌───────────────┐  │
│  │ HMAC Security │──>│ Pydantic v2   │  │
│  │ Verification  │   │ Validation    │  │
│  └───────────────┘   └───────────────┘  │
└─────────────────────────────────────────┘
          │ (Validated & Clean Payload)
          ▼
[Downstream CRM / n8n Automation Workflows]
