from contextlib import contextmanager
from typing import Literal
from uuid import uuid4, UUID

from lucy.session.repository import SessionRepository, SessionStore
from lucy.session.models import (
    SessionMetadata,
    TranscriptEvent,
    SessionData,
    SessionSummary,
    SessionsList,
    UsageMetrics,
)
from lucy.session.vars import session_id_var, request_id_var


class SessionManager:
    def __init__(self):
        self._repository = SessionRepository()
        self._store: SessionStore = None

    @contextmanager
    def request_scope(self):
        request_id = uuid4()
        token = request_id_var.set(request_id)

        try:
            yield
        finally:
            request_id_var.reset(token)

    @contextmanager
    def session_scope(self):
        session_id = uuid4()
        token = session_id_var.set(session_id)

        self._store = self._repository.open_session(session_id)
        self.metadata = self._store.read_metadata()

        try:
            yield
        finally:
            self._store.close()
            self._store = None
            session_id_var.reset(token)

    # ---------- Transcript ----------

    def append_transcript(
        self, 
        role: Literal["user", "agent"],
        message: str
    ) -> None:
        self._require_store()
        event = TranscriptEvent(role=role, message=message)
        self._store.append_transcript(event)

    def get_transcript(self) -> list[TranscriptEvent]:
        self._require_store()
        return self._store.read_transcript_data()

    # ---------- Metadata ----------

    def update_metadata(
        self, 
        model_id: str,
        usage: UsageMetrics
    ):
        self._require_store()
        metadata = self.get_metadata()
        if model_id not in metadata.usage:
            metadata.usage[model_id] = UsageMetrics()
        metadata.usage[model_id] += usage
        self._store.update_metadata(metadata)

    def get_metadata(self) -> SessionMetadata:
        self._require_store()
        return self._store.read_metadata()

    # ---------- Session ----------

    def session(self) -> SessionData:
        self._require_store()
        return self._store.read_session_data()

    def list_sessions(self, limit: int = 10) -> SessionsList:
        return self._repository.list_sessions(limit)

    # ---------- Helpers ----------

    @property
    def session_id(self) -> UUID | None:
        sid = session_id_var.get()
        return sid if sid != "-" else None

    @property
    def request_id(self) -> UUID | None:
        rid = request_id_var.get()
        return rid if rid != "-" else None

    def _require_store(self):
        if self._store is None:
            raise RuntimeError(
                "No active session. Use 'with session_manager.session_scope():' first."
            )