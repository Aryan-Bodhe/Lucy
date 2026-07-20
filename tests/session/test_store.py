import json
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from lucy.session.models import (
    ExecutionMetrics,
    SessionMetadata,
    TranscriptEvent,
    UsageMetrics,
)
from lucy.session.store import SessionStore


@pytest.fixture
def store(tmp_path):
    session_id = uuid4()

    session_dir = tmp_path / str(session_id)
    session_dir.mkdir()

    metadata_file = session_dir / "metadata.json"
    transcript_file = session_dir / "transcript.jsonl"

    metadata = SessionMetadata()

    metadata_file.write_text(
        metadata.model_dump_json(indent=2),
        encoding="utf-8",
    )

    transcript_file.touch()

    return SessionStore(
        session_id=session_id,
        session_dir=session_dir,
        metadata_file=metadata_file,
        transcript_file=transcript_file,
    )


def test_append_transcript(store):
    event = TranscriptEvent(
        timestamp=datetime.now(UTC),
        role="user",
        message="hello",
    )

    store.append_transcript(event)

    lines = store.transcript_file.read_text(encoding="utf-8").splitlines()

    assert len(lines) == 1

    loaded = TranscriptEvent.model_validate_json(lines[0])

    assert loaded == event


def test_update_metadata(store):
    metadata = SessionMetadata(
        usage=UsageMetrics(input_tokens=123),
        execution=ExecutionMetrics(model_calls=5),
    )

    store.update_metadata(metadata)

    loaded = SessionMetadata.model_validate_json(
        store.metadata_file.read_text(encoding="utf-8")
    )

    assert loaded == metadata


def test_load(store):
    event = TranscriptEvent(
        timestamp=datetime.now(UTC),
        role="lucy",
        message="hi",
    )

    store.append_transcript(event)

    expected_metadata = SessionMetadata.model_validate_json(
        store.metadata_file.read_text(encoding="utf-8")
    )

    data = store.load()

    assert data.session_id == store.session_id
    assert data.metadata == expected_metadata
    assert data.transcript == [event]


def test_validate_success(store):
    store.validate()


def test_validate_missing_metadata(store):
    store.metadata_file.unlink()

    with pytest.raises(FileNotFoundError):
        store.validate()


def test_validate_missing_transcript(store):
    store.transcript_file.unlink()

    with pytest.raises(FileNotFoundError):
        store.validate()


def test_validate_invalid_metadata_json(store):
    store.metadata_file.write_text(
        "{invalid json",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        store.validate()


def test_validate_invalid_metadata_schema(store):
    store.metadata_file.write_text(
        json.dumps({"foo": "bar"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        store.validate()


def test_validate_invalid_transcript_json(store):
    store.transcript_file.write_text(
        "{bad json}\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        store.validate()


def test_validate_invalid_transcript_schema(store):
    store.transcript_file.write_text(
        json.dumps({"foo": "bar"}) + "\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError):
        store.validate()