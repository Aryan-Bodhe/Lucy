import uuid
from datetime import UTC, datetime

import pytest

from lucy.session import models as session_models
from lucy.session import repository as repository_module
from lucy.session import store as store_module
from lucy.session import manager as manager_module


@pytest.fixture()
def sessions_dir(tmp_path, monkeypatch):
    path = tmp_path / "sessions"
    path.mkdir()
    monkeypatch.setattr(store_module, "SESSIONS_DIR", path)
    monkeypatch.setattr(repository_module, "SESSIONS_DIR", path)
    monkeypatch.setattr(manager_module, "SessionRepository", repository_module.SessionRepository)
    return path


@pytest.fixture()
def session_id():
    return uuid.uuid4()


@pytest.fixture()
def fixed_timestamp():
    return datetime(2026, 7, 29, 11, 36, tzinfo=UTC)


@pytest.fixture()
def sample_metadata(fixed_timestamp):
    return session_models.SessionMetadata(
        started_at=fixed_timestamp,
        ended_at=fixed_timestamp,
        usage=session_models.UsageMetrics(
            input_tokens=12,
            output_tokens=34,
            cached_input_tokens=5,
            cached_output_tokens=6,
            cost_usd=0.42,
        ),
        execution=session_models.ExecutionMetrics(
            model_calls=3,
            tool_calls=4,
            turns=5,
            models_used={"gpt-5.4-mini", "o3"},
        ),
    )


@pytest.fixture()
def sample_event(fixed_timestamp):
    return session_models.TranscriptEvent(
        timestamp=fixed_timestamp,
        role="user",
        message="hello",
    )


@pytest.fixture()
def sample_transcript(sample_event):
    return session_models.SessionTranscript(events=[sample_event])
