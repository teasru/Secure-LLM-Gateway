from pydantic import BaseModel, Field
from typing import Literal


# ============================================================
# LLM Request / Response Models
# ============================================================

class GenerateRequest(BaseModel):
    prompt: str = Field(
        ...,
        min_length=1,
        description="User prompt sent to the LLM"
    )
    max_tokens: int = Field(
        default=200,
        ge=1,
        le=1000,
        description="Maximum number of tokens to generate"
    )


class GenerateResponse(BaseModel):
    response: str = Field(
        ...,
        description="LLM-generated response"
    )


# ============================================================
# Authentication Models
# ============================================================

class TokenRequest(BaseModel):
    user_id: str = Field(
        ...,
        min_length=1,
        description="Unique user identifier"
    )
    role: Literal["user", "admin"] = Field(
        ...,
        description="User role"
    )


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ============================================================
# Health Check Model
# ============================================================

class HealthResponse(BaseModel):
    status: str = Field(
        ...,
        description="Service health status"
    )
