from datetime import UTC, datetime

import pytest

from lucy.session.models import SessionMetadata, UsageMetrics


class DummyStore:
    def __init__(self):
        self.appended = []
        self.metadata_updates = []
        self.closed = False
        self._metadata = SessionMetadata(started_at=datetime(2026, 7, 29, 11, 0, tzinfo=UTC))
        self._transcript = []

    def append_transcript(self, event):
        self.appended.append(event)
        self._transcript.append(event)

    def update_metadata(self, metadata):
        self.metadata_updates.append(metadata)
        self._metadata = metadata

    def read_metadata(self):
        return self._metadata.model_copy(deep=True)

    def read_transcript_data(self):
        return self._transcript

    def read_session_data(self):
        return {"metadata": self._metadata, "transcript": self._transcript}

    def close(self):
        self.closed = True


class DummyRepo:
    def __init__(self):
        self.opened = []
        self.sessions = []

    def open_session(self, session_id):
        self.opened.append(session_id)
        return DummyStore()

    def list_sessions(self, limit=5):
        return self.sessions[:limit]


@pytest.fixture()
def manager(monkeypatch):
    from lucy.session import manager as manager_module

    monkeypatch.setattr(manager_module, "SessionRepository", DummyRepo)
    return manager_module.SessionManager()


def test_request_scope_sets_and_resets_request_id(manager):
    assert manager.request_id is None
    with manager.request_scope():
        assert manager.request_id is not None
    assert manager.request_id is None


def test_session_scope_opens_and_closes_store(manager):
    assert manager.session_id is None
    with manager.session_scope():
        store = manager._store
        assert manager.session_id is not None
        assert manager._repository.opened == [manager.session_id]
    assert store.closed is True
    assert manager.session_id is None
    assert manager._store is None


def test_session_scope_closes_store_when_body_raises(manager):
    with pytest.raises(RuntimeError):
        with manager.session_scope():
            store = manager._store
            raise RuntimeError("boom")
    assert store.closed is True
    assert manager.session_id is None


def test_append_transcript_requires_active_session(manager):
    with pytest.raises(RuntimeError):
        manager.append_transcript(role="user", message="hi")


def test_append_transcript_builds_event_for_store(manager):
    with manager.session_scope():
        manager.append_transcript(role="user", message="hi")
        (event,) = manager._store.appended

    assert event.role == "user"
    assert event.message == "hi"


def test_update_metadata_sums_per_turn_usage_per_model(manager):
    turn = UsageMetrics(input_tokens=10, output_tokens=2, total_tokens=12, cost_usd=0.5)

    with manager.session_scope():
        manager.update_metadata(model_id="gpt-test", usage=turn)
        manager.update_metadata(model_id="gpt-test", usage=turn)
        manager.update_metadata(model_id="other", usage=turn)
        usage = manager.get_metadata().usage

    assert usage["gpt-test"].input_tokens == 20
    assert usage["gpt-test"].cost_usd == 1.0
    assert usage["other"].input_tokens == 10


def test_read_methods_delegate_to_store(manager):
    with manager.session_scope():
        manager.append_transcript(role="user", message="hi")
        (event,) = manager.get_transcript()
        assert event.message == "hi"
        assert manager.get_metadata().started_at == datetime(2026, 7, 29, 11, 0, tzinfo=UTC)
        assert manager.session()["transcript"] == [event]


def test_list_sessions_delegates_to_repository(manager):
    manager._repository.sessions = [1, 2, 3]

    assert manager.list_sessions(limit=2) == [1, 2]
