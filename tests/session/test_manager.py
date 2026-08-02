from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from lucy.session.models import SessionMetadata, TranscriptEvent


class DummyStore:
    def __init__(self):
        self.appended = []
        self.metadata_updates = []
        self._metadata = SessionMetadata(started_at=datetime(2026, 7, 29, 11, 0, tzinfo=UTC))
        self._transcript = []

    def append_transcript(self, event):
        self.appended.append(event)
        self._transcript.append(event)

    def update_metadata(self, metadata):
        self.metadata_updates.append(metadata)
        self._metadata = metadata

    def read_metadata(self):
        return self._metadata

    def read_transcript_data(self):
        return self._transcript

    def read_session_data(self):
        return {"metadata": self._metadata, "transcript": self._transcript}


class DummyRepo:
    def __init__(self):
        self.created = []
        self.sessions = []

    def open_session(self, session_id):
        store = DummyStore()
        self.created.append(session_id)
        return store


    def list_sessions(self, limit=5):
        return self.sessions[:limit]


def _patch_manager(monkeypatch):
    from lucy.session import manager as manager_module

    monkeypatch.setattr(manager_module, "SessionRepository", DummyRepo)
    return manager_module


def test_request_scope_sets_and_resets_request_id(monkeypatch):
    manager_module = _patch_manager(monkeypatch)
    manager = manager_module.SessionManager()

    assert manager.request_id is None
    with manager.request_scope():
        assert manager.request_id is not None
    assert manager.request_id is None


def test_session_scope_sets_and_resets_session_id(monkeypatch):
    manager_module = _patch_manager(monkeypatch)
    manager = manager_module.SessionManager()

    assert manager.session_id is None
    with manager.session_scope():
        assert manager.session_id is not None
        assert manager._store is not None
    assert manager.session_id is None
    assert manager._store is None


def test_append_transcript_requires_active_session(monkeypatch):
    manager_module = _patch_manager(monkeypatch)
    manager = manager_module.SessionManager()

    with pytest.raises(RuntimeError):
        manager.append_transcript(
            TranscriptEvent(
                timestamp=datetime(2026, 7, 29, 11, 0, tzinfo=UTC),
                role="user",
                message="hi",
            )
        )


def test_append_transcript_and_metadata_delegate_to_store(monkeypatch):
    manager_module = _patch_manager(monkeypatch)
    manager = manager_module.SessionManager()

    event = TranscriptEvent(
        timestamp=datetime(2026, 7, 29, 11, 0, tzinfo=UTC),
        role="user",
        message="hi",
    )
    metadata = SessionMetadata(started_at=datetime(2026, 7, 29, 11, 0, tzinfo=UTC))

    with manager.session_scope():
        manager.append_transcript(event)
        manager.update_metadata(metadata)

        assert manager._store.appended == [event]
        assert manager._store.metadata_updates == [metadata]


def test_read_methods_delegate_to_store(monkeypatch):
    manager_module = _patch_manager(monkeypatch)
    manager = manager_module.SessionManager()

    event = TranscriptEvent(
        timestamp=datetime(2026, 7, 29, 11, 0, tzinfo=UTC),
        role="user",
        message="hi",
    )

    with manager.session_scope():
        manager.append_transcript(event)
        assert manager.get_transcript() == [event]
        assert manager.get_metadata().started_at == datetime(2026, 7, 29, 11, 0, tzinfo=UTC)
        assert manager.session()["transcript"] == [event]



def test_list_sessions_delegates_to_repository(monkeypatch):
    manager_module = _patch_manager(monkeypatch)
    manager = manager_module.SessionManager()

    expected = [1, 2, 3]
    manager._repository.sessions = expected

    assert manager.list_sessions(limit=2) == [1, 2]


def test_session_scope_uses_repository_open_session_or_legacy_method(monkeypatch):
    from lucy.session import manager as manager_module

    class RepoWithOnlyOpenSession:
        def __init__(self):
            self.called = False

        def open_session(self, session_id):
            self.called = True
            return DummyStore()

        def list_sessions(self, limit=5):
            return []

    monkeypatch.setattr(manager_module, "SessionRepository", RepoWithOnlyOpenSession)
    manager = manager_module.SessionManager()

    # This documents the intended contract: if you keep the current code calling
    # get_or_create_session, this test will fail until the manager is aligned.
    with manager.session_scope():
        assert manager._store is not None
