# Secure LLM Gateway with Policy Engine

A production-style, modular backend service that acts as a secure gateway in front of a Large Language Model (LLM).

This system enforces authentication, role-based access control, rate limiting, prompt inspection, output filtering, caching, and observability before allowing access to an LLM provider.

It is designed as a **modular monolith** with clear service boundaries and production-aligned structure.

---

## Overview

This project implements a secure AI gateway layer between clients and an LLM API.

Instead of directly exposing a model endpoint, all requests pass through:

```
Client
   ↓
JWT Authentication
   ↓
RBAC
   ↓
Rate Limiter (Redis)
   ↓
Prompt Inspection
   ↓
Policy Engine
   ↓
Cache Layer (Redis)
   ↓
LLM Provider (OpenAI / Local Fallback)
   ↓
Output Filtering
   ↓
Structured Logging + Tracing
   ↓
Response
```

The goal is to simulate real-world AI governance and infrastructure patterns used in production systems.

---

## Architecture

This is implemented as a **modular monolith**, not microservices.

All components run in a single FastAPI application, but are separated into modules:

```
app/
├── auth/          # JWT handling and RBAC
├── core/          # Rate limiting, caching, policy engine, filtering
├── llm/           # OpenAI client + fallback
├── logging/       # Structured JSON logging
├── admin/         # Policy update routes
├── models.py      # Pydantic schemas
├── config.py      # Environment-based configuration
├── dependencies.py
└── main.py        # Application entrypoint
```

The design allows future decomposition into microservices if scaling demands it.

---

## Features

### JWT Authentication

* Stateless authentication using signed JWT tokens
* Tokens include `user_id` and `role`
* Signature validated on every request

---

### Role-Based Access Control (RBAC)

* Roles: `user`, `admin`
* Endpoint access enforced via dependency injection
* Strongly typed role validation using `Literal`

---

### Redis Rate Limiting

* Per-user request limits
* Configurable via environment variables
* Fixed window rate limiting
* Fail-open behavior if Redis is unavailable

---

### Prompt Inspection

Prevents common prompt injection attempts such as:

* “ignore previous instructions”
* “reveal system prompt”
* Suspicious patterns defined in policy

---

### Policy Engine

Policies are:

* Stored in Redis
* Updatable via `/admin/policy`
* Loaded dynamically at runtime

This simulates AI governance control planes.

---

### Redis Caching

* SHA256-based cache keys
* Includes prompt + max_tokens
* Reduces repeated LLM calls
* Improves response latency

---

### Output Filtering

* Redacts sensitive keywords
* Detects possible secret patterns
* Applies post-processing guardrails

---

### OpenTelemetry Tracing

* Request-level spans
* LLM call spans
* Fallback spans
* Latency measurement

Ready for integration with tracing backends like Jaeger or Datadog.

---

### Structured JSON Logging

All events are logged in structured format:

* cache hits
* blocked prompts
* request completion
* LLM provider used
* latency

Designed for ingestion by log aggregation systems.

---

### Health Endpoint

`GET /health`

Used for:

* Load balancers
* Uptime checks
* Infrastructure monitoring

Returns:

```json
{
  "status": "ok"
}
```

---

## API Endpoints

### `POST /login`

Generates a JWT token.

```json
{
  "user_id": "string",
  "role": "admin"
}
```

---

### `POST /generate`

Protected endpoint requiring Bearer token.

```json
{
  "prompt": "Explain Redis simply",
  "max_tokens": 100
}
```

---

## Environment Configuration

Create a `.env` file locally:


This service relies on environment variables for configuration and secret management.

Create a local `.env` file in the project root with the following variables:

```bash
OPENAI_API_KEY=your_openai_api_key_here
JWT_SECRET=your_jwt_secret_here
REDIS_HOST=localhost
RATE_LIMIT=10
RATE_WINDOW=60
```

### Explanation

| Variable         | Description                                    |
| ---------------- | ---------------------------------------------- |
| `OPENAI_API_KEY` | API key used to call the OpenAI provider       |
| `JWT_SECRET`     | Secret used to sign and verify JWT tokens      |
| `REDIS_HOST`     | Redis hostname (default: localhost)            |
| `RATE_LIMIT`     | Maximum number of requests per user per window |
| `RATE_WINDOW`    | Rate limiting window in seconds                |

---

## Running the Project

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 3. Start Redis

```bash
redis-server
```

(or use Docker)

---

### 4. Run the Application

```bash
uvicorn app.main:app --reload
```

Access Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

## Design Decisions

### Modular Monolith

Chosen over microservices to:

* Reduce operational complexity
* Maintain clear service boundaries
* Allow future service extraction

---

### Stateless JWT Auth

Avoids session storage and supports horizontal scaling.

---

### Redis for Rate Limiting & Caching

Redis provides:

* Atomic counters
* TTL support
* Low latency
* Production alignment

---

### Fail-Open Rate Limiting

If Redis fails, requests are not blocked.
Prevents cascading system failure.

---

### Typed API Contracts

All requests and responses are defined using Pydantic models.
This generates:

* Automatic OpenAPI documentation
* Runtime validation
* Strong API contracts


