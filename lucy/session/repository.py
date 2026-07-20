import json
from pathlib import Path
from uuid import UUID

from lucy.config import SESSIONS_DIR
from lucy.session.models import SessionMetadata, SessionSummary
from lucy.session.store import SessionStore


class SessionRepository:
    def __init__(self):
        self.sessions_dir = Path(SESSIONS_DIR)

    def get_all_sessions(self, limit: int = 5) -> list[SessionSummary]:
        sessions = []
        for path in self.sessions_dir.iterdir():
            session_id = UUID(path.name)
            metadata_file = path / "metadata.json"
            with metadata_file.open("r", encoding="utf-8") as f:
                metadata_dict = json.load(f)
            metadata = SessionMetadata(**metadata_dict)

            sessions.append(
                SessionSummary(session_id=session_id, metadata=metadata)
            )
        sorted_sessions = sorted(sessions, key=lambda s: s.metadata.started_at, reverse=True)
        return sorted_sessions[:limit]

    def create(self, session_id: UUID):
        session_dir = self.sessions_dir / f"{session_id}"
        metadata_file = session_dir / "metadata.json"
        transcript_file = session_dir / "transcript.jsonl"

        session_dir.mkdir(parents=True, exist_ok=True)
        transcript_file.touch(exist_ok=False)
        metadata_file.touch(exist_ok=False)
        default_metadata = SessionMetadata()
        metadata_file.write_text(
            default_metadata.model_dump_json(indent=2),
            encoding="utf-8"
        )

        return SessionStore(
            session_id=session_id, 
            session_dir=session_dir, 
            metadata_file=metadata_file, 
            transcript_file=transcript_file
        )
