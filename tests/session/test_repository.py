import json
from datetime import UTC, datetime, timedelta
from uuid import uuid4

import pytest

from lucy.session.models import SessionMetadata
from lucy.session.repository import SessionRepository

@pytest.fixture
def repo(tmp_path, monkeypatch):
    monkeypatch.setattr(
        "lucy.session.repository.SESSIONS_DIR",
        tmp_path,
    )
    return SessionRepository()


def test_create_creates_session(repo):
    session_id = uuid4()

    store = repo.create(session_id)

    session_dir = repo.sessions_dir / str(session_id)

    assert session_dir.exists()
    assert (session_dir / "metadata.json").exists()
    assert (session_dir / "transcript.jsonl").exists()

    assert store.session_id == session_id


def test_create_writes_default_metadata(repo):
    session_id = uuid4()

    repo.create(session_id)

    metadata_file = (
        repo.sessions_dir
        / str(session_id)
        / "metadata.json"
    )

    metadata = SessionMetadata.model_validate_json(
        metadata_file.read_text()
    )

    assert metadata.ended_at is None
    assert metadata.execution.model_calls == 0
    assert metadata.execution.tool_calls == 0
    assert metadata.usage.input_tokens == 0


def test_get_all_sessions_returns_sessions(repo):
    repo.create(uuid4())
    repo.create(uuid4())

    sessions = repo.get_all_sessions()

    assert len(sessions) == 2

def test_get_all_sessions_sorted_by_started_at(repo):
    old_id = uuid4()
    new_id = uuid4()

    repo.create(old_id)
    repo.create(new_id)

    old_meta_file = (
        repo.sessions_dir
        / str(old_id)
        / "metadata.json"
    )

    new_meta_file = (
        repo.sessions_dir
        / str(new_id)
        / "metadata.json"
    )

    old = SessionMetadata(
        started_at=datetime.now(UTC) - timedelta(days=1)
    )

    new = SessionMetadata(
        started_at=datetime.now(UTC)
    )

    old_meta_file.write_text(old.model_dump_json(indent=2))
    new_meta_file.write_text(new.model_dump_json(indent=2))

    sessions = repo.get_all_sessions()

    assert sessions[0].session_id == new_id
    assert sessions[1].session_id == old_id


def test_get_all_sessions_limit(repo):
    for _ in range(10):
        repo.create(uuid4())

    sessions = repo.get_all_sessions(limit=3)

    assert len(sessions) == 3


def test_create_existing_session_raises(repo):
    session_id = uuid4()

    repo.create(session_id)

    with pytest.raises(FileExistsError):
        repo.create(session_id)


def test_get_all_sessions_invalid_uuid_raises(repo):
    (repo.sessions_dir / "not-a-session").mkdir()

    with pytest.raises(ValueError):
        repo.get_all_sessions()