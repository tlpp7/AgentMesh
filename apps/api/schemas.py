"""Typed request/response contracts for the optional R1 API."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, field_validator

class RunRequest(BaseModel):
    model_config=ConfigDict(extra="forbid")
    objective: str = Field(min_length=1,max_length=5000)
    attempts: int = Field(default=3,ge=1,le=10,strict=True)
    contains: str | None = Field(default=None,max_length=1000)

    @field_validator("objective")
    @classmethod
    def nonblank(cls,value):
        if not value.strip():raise ValueError("objective must not be blank")
        return value

class ErrorResponse(BaseModel):
    error: str
    message: str | None = None

class HealthResponse(BaseModel):
    status: Literal["ok"]="ok"
    adapter: Literal["fastapi"]="fastapi"
    legacy_preserved: bool=True
