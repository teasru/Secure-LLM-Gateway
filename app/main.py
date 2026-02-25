from fastapi import FastAPI, Depends, HTTPException
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
import time

# ---- Internal Imports ----
from app.models import (
    GenerateRequest,
    GenerateResponse,
    TokenRequest,
    TokenResponse,
    HealthResponse,   # ← Added
)
from app.dependencies import get_current_user
from app.auth.jwt_handler import create_token
from app.auth.rbac import check_role
from app.core.rate_limiter import enforce_rate_limit
from app.core.prompt_inspector import inspect_prompt
from app.core.cache import get_cache, set_cache
from app.core.output_filter import filter_output
from app.llm.openai_client import call_openai
from app.llm.local_fallback import call_local_model
from app.logging.logger import log_event
from app.admin.routes import router as admin_router


# ============================================================
# FastAPI App Initialization
# ============================================================

app = FastAPI(title="Secure LLM Gateway")
app.include_router(admin_router, prefix="/admin")


# ============================================================
# OpenTelemetry Setup
# ============================================================

trace.set_tracer_provider(TracerProvider())
span_processor = BatchSpanProcessor(ConsoleSpanExporter())
trace.get_tracer_provider().add_span_processor(span_processor)

FastAPIInstrumentor.instrument_app(app)
tracer = trace.get_tracer(__name__)


# ============================================================
# Health Check Endpoint
# ============================================================

@app.get("/health", response_model=HealthResponse)
def health():
    """
    Basic health check.
    Used by load balancers, monitoring systems, uptime checks.
    """
    return {"status": "ok"}


# ============================================================
# Authentication Endpoint
# ============================================================

@app.post("/login", response_model=TokenResponse)
def login(request: TokenRequest):
    """
    Demo login endpoint.
    In production, validate credentials properly.
    """
    token = create_token(request.user_id, request.role)
    return {
        "access_token": token,
        "token_type": "bearer",
    }


# ============================================================
# Main Secure LLM Endpoint
# ============================================================

@app.post("/generate", response_model=GenerateResponse)
def generate(
    request_body: GenerateRequest,
    user=Depends(get_current_user),
):
    """
    Secure LLM Gateway:
    - JWT Authentication
    - RBAC
    - Rate limiting
    - Prompt inspection
    - Redis caching
    - Output filtering
    - Structured logging
    - Distributed tracing
    """

    prompt = request_body.prompt
    max_tokens = request_body.max_tokens

    with tracer.start_as_current_span("generate_request") as span:

        start_time = time.time()
        llm_provider = "unknown"

        span.set_attribute("user.id", user["sub"])
        span.set_attribute("user.role", user["role"])

        # ------------------------------------------------
        # 1️⃣ Rate Limiting
        # ------------------------------------------------
        enforce_rate_limit(user["sub"])

        # ------------------------------------------------
        # 2️⃣ Role-Based Access Control
        # ------------------------------------------------
        if not check_role(user["role"], ["user", "admin"]):
            span.set_status(Status(StatusCode.ERROR))
            raise HTTPException(status_code=403, detail="Insufficient permissions")

        # ------------------------------------------------
        # 3️⃣ Cache Lookup
        # ------------------------------------------------
        cache_key = f"{prompt}:{max_tokens}"
        cached = get_cache(cache_key)

        if cached:
            span.set_attribute("cache.hit", True)

            log_event({
                "event": "cache_hit",
                "user": user["sub"],
                "role": user["role"],
                "prompt_preview": prompt[:50],
            })

            return {"response": cached}

        span.set_attribute("cache.hit", False)

        # ------------------------------------------------
        # 4️⃣ Prompt Inspection
        # ------------------------------------------------
        safe, reason = inspect_prompt(prompt)
        if not safe:
            span.set_status(Status(StatusCode.ERROR))

            log_event({
                "event": "blocked_prompt",
                "reason": reason,
                "user": user["sub"],
            })

            raise HTTPException(status_code=403, detail=reason)

        # ------------------------------------------------
        # 5️⃣ LLM Call (Primary + Fallback)
        # ------------------------------------------------
        try:
            with tracer.start_as_current_span("openai_call"):
                response = call_openai(prompt, max_tokens)
                llm_provider = "openai"

        except Exception as e:
            with tracer.start_as_current_span("local_fallback"):
                response = call_local_model(prompt)
                llm_provider = "local"
                span.set_attribute("fallback_reason", str(e))

        span.set_attribute("llm.provider", llm_provider)

        # ------------------------------------------------
        # 6️⃣ Output Filtering
        # ------------------------------------------------
        response = filter_output(response)

        # ------------------------------------------------
        # 7️⃣ Cache Store
        # ------------------------------------------------
        set_cache(cache_key, response)

        # ------------------------------------------------
        # 8️⃣ Structured Logging
        # ------------------------------------------------
        latency = round(time.time() - start_time, 3)

        log_event({
            "event": "request_complete",
            "user": user["sub"],
            "role": user["role"],
            "latency_seconds": latency,
            "prompt_preview": prompt[:50],
            "llm_provider": llm_provider,
        })

        span.set_attribute("request.latency_seconds", latency)

        return {"response": response}
