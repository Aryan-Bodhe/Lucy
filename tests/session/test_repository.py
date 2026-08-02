from datetime import UTC, datetime
from uuid import uuid4

import pytest

from lucy.session.models import SessionMetadata
from lucy.session.repository import SessionRepository


def _make_session_dir(base, session_id, started_at):
    path = base / str(session_id)
    path.mkdir(parents=True, exist_ok=True)
    metadata = SessionMetadata(started_at=started_at)
    (path / "metadata.json").write_text(metadata.model_dump_json(indent=2), encoding="utf-8")
    (path / "transcript.jsonl").write_text("", encoding="utf-8")
    return path


def test_open_session_initialises_store_and_files(sessions_dir):
    repo = SessionRepository()
    session_id = uuid4()

    store = repo.open_session(session_id)

    assert store.session_id == session_id
    assert store.path.exists()
    assert store.metadata_file.exists()
    assert store.transcript_file.exists()


def test_get_metadata_returns_summary(sessions_dir):
    repo = SessionRepository()
    session_id = uuid4()
    started_at = datetime(2026, 7, 29, 9, 0, tzinfo=UTC)
    _make_session_dir(sessions_dir, session_id, started_at)

    summary = repo._get_session_summary(sessions_dir / str(session_id))

    assert summary.session_id == session_id
    assert summary.metadata.started_at == started_at


def test_list_sessions_sorts_by_started_at_and_applies_limit(sessions_dir):
    repo = SessionRepository()

    older = uuid4()
    middle = uuid4()
    newer = uuid4()

    _make_session_dir(sessions_dir, newer, datetime(2026, 7, 29, 12, 0, tzinfo=UTC))
    _make_session_dir(sessions_dir, older, datetime(2026, 7, 29, 8, 0, tzinfo=UTC))
    _make_session_dir(sessions_dir, middle, datetime(2026, 7, 29, 10, 0, tzinfo=UTC))

    sessions = repo.list_sessions(limit=2)

    assert [s.session_id for s in sessions] == [older, middle]



def test_list_sessions_respects_hard_limit(sessions_dir):
    repo = SessionRepository()
    repo.ITERDIR_HARD_LIMIT = 1

    ids = [uuid4() for _ in range(4)]
    for index, sid in enumerate(ids):
        _make_session_dir(
            sessions_dir,
            sid,
            datetime(2026, 7, 29, 8 + index, 0, tzinfo=UTC),
        )

    sessions = repo.list_sessions(limit=10)

    assert len(sessions) == 2
