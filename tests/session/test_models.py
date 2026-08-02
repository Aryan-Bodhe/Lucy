from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from lucy.session.models import (
    SessionData,
    SessionMetadata,
    SessionSummary,
    SessionTranscript,
    TranscriptEvent,
    UsageMetrics,
)


def test_usage_metrics_defaults():
    metrics = UsageMetrics()
    assert metrics.input_tokens == 0
    assert metrics.output_tokens == 0
    assert metrics.cached_input_tokens == 0
    assert metrics.cached_output_tokens == 0
    assert metrics.cost_usd == 0.0


def test_transcript_event_accepts_valid_role():
    event = TranscriptEvent(
        timestamp=datetime(2026, 7, 29, 11, 36, tzinfo=UTC),
        role="lucy",
        message="done",
    )
    assert event.role == "lucy"


def test_transcript_event_rejects_invalid_role():
    with pytest.raises(ValidationError):
        TranscriptEvent(
            timestamp=datetime(2026, 7, 29, 11, 36, tzinfo=UTC),
            role="assistant",  # type: ignore[arg-type]
            message="nope",
        )


def test_session_metadata_defaults():
    metadata = SessionMetadata()
    assert metadata.ended_at is None
    assert isinstance(metadata.started_at, datetime)
    assert metadata.usage == UsageMetrics()


def test_session_metadata_forbids_extra_fields():
    with pytest.raises(ValidationError):
        SessionMetadata.model_validate({"unexpected": 1})


def test_session_transcript_wraps_events():
    event = TranscriptEvent(
        timestamp=datetime(2026, 7, 29, 11, 36, tzinfo=UTC),
        role="user",
        message="hello",
    )
    transcript = SessionTranscript(events=[event])
    assert transcript.events == [event]


def test_session_data_and_summary_round_trip(session_id):
    metadata = SessionMetadata()
    event = TranscriptEvent(
        timestamp=datetime(2026, 7, 29, 11, 36, tzinfo=UTC),
        role="user",
        message="hello",
    )
    transcript = SessionTranscript(events=[event])

    session_data = SessionData(session_id=session_id, metadata=metadata, transcript=transcript)
    summary = SessionSummary(session_id=session_id, metadata=metadata)

    assert session_data.session_id == session_id
    assert session_data.transcript.events == [event]
    assert summary.session_id == session_id
