from concurrent.futures import ThreadPoolExecutor
from uuid import UUID
from pathlib import Path
from lucy.config import SESSIONS_DIR
from lucy.session.models import SessionSummary, SessionMetadata, SessionsList
from lucy.session.store import SessionStore

class SessionRepository:
    def __init__(self):
        self.path = SESSIONS_DIR
        self.ITERDIR_HARD_LIMIT = 50

    def open_session(self, session_id: UUID):
        session = SessionStore(session_id)
        session.initialise()
        return session

    def _get_session_summary(self, dir: Path):
        session_id = UUID(dir.name)
        session = SessionStore(session_id)
        metadata = session.read_metadata()
        return SessionSummary(session_id=session_id, metadata=metadata)


    def list_sessions(self, limit: int = 10):
        sessions: list[SessionSummary] = []
        i = 0
        for dir in self.path.iterdir():
            if i >= self.ITERDIR_HARD_LIMIT:
                break
            i += 1
            sessions.append(self._get_session_summary(dir))
            
        sorted_sessions = sorted(
            sessions, 
            key=lambda x: x.metadata.started_at,
            reverse=True
        )
        return SessionsList(
            sessions=sorted_sessions[:limit],
            total_count=len(sorted_sessions),
            requested_count=limit
        )
    
