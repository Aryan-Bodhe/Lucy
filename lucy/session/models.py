from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class UsageMetrics(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0
    cached_output_tokens: int = 0
    cost_usd: float = 0.0


class ExecutionMetrics(BaseModel):
    model_calls: int = 0
    tool_calls: int = 0
    turns: int = 0
    models_used: set[str] = Field(default_factory=set)


class TranscriptEvent(BaseModel):
    timestamp: datetime
    role: Literal["user", "lucy"]
    message: str

class SessionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    ended_at: datetime | None = None

    usage: UsageMetrics = Field(default_factory=UsageMetrics)
    execution: ExecutionMetrics = Field(default_factory=ExecutionMetrics)


class SessionData(BaseModel):
    session_id: UUID
    metadata: SessionMetadata
    transcript: list[TranscriptEvent]


class SessionSummary(BaseModel):
    session_id: UUID
    metadata: SessionMetadata
