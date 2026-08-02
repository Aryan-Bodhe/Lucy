from datetime import UTC, datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class UsageMetrics(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    cached_input_tokens: int = 0
    cached_output_tokens: int = 0
    context_used_pct: float = 0.0
    cost_usd: float = 0.0

    def __add__(self, other: "UsageMetrics") -> "UsageMetrics":
        if not isinstance(other, UsageMetrics):
            return NotImplemented

        return UsageMetrics(
            input_tokens=self.input_tokens + other.input_tokens,
            output_tokens=self.output_tokens + other.output_tokens,
            total_tokens=self.total_tokens + other.total_tokens,
            cached_input_tokens=self.cached_input_tokens + other.cached_input_tokens,
            cached_output_tokens=self.cached_output_tokens + other.cached_output_tokens,
            context_used_pct=max(self.context_used_pct, other.context_used_pct),
            cost_usd=self.cost_usd + other.cost_usd,
        )

class TranscriptEvent(BaseModel):
    timestamp: datetime = Field(default_factory=lambda x: datetime.now(UTC))
    role: Literal["user", "agent"]
    message: str

class SessionTranscript(BaseModel):
    events: list[TranscriptEvent]

class SessionMetadata(BaseModel):
    model_config = ConfigDict(extra="forbid")
    started_at: datetime
    ended_at: datetime | None = None
    usage: dict[str, UsageMetrics] = Field(default_factory=dict)


class SessionData(BaseModel):
    session_id: UUID
    metadata: SessionMetadata
    transcript: SessionTranscript


class SessionSummary(BaseModel):
    session_id: UUID
    metadata: SessionMetadata

class SessionsList(BaseModel):
    sessions: list[SessionSummary]
    total_count: int
    requested_count: int