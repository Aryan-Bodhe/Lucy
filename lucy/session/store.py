from datetime import UTC, datetime
import json
from uuid import UUID

from lucy.config import SESSIONS_DIR
from lucy.session.models import SessionData, SessionMetadata, SessionTranscript, TranscriptEvent
from lucy.logger import get_logger

logger = get_logger(__name__)


class SessionStore:
    def __init__(self, session_id: UUID):
        self.session_id = session_id
        self.path = SESSIONS_DIR / f"{session_id}"
        self.metadata_file = self.path / "metadata.json"
        self.transcript_file = self.path / "transcript.jsonl"
        

    def initialise(self):
        self.path.mkdir(exist_ok=True, parents=True)
        self.metadata_file.touch(exist_ok=True)
        self.update_metadata(
            SessionMetadata(started_at=datetime.now(UTC))
        )

        self.transcript_file.touch(exist_ok=True)
        logger.info("[store.py] Store init successful.")
        return self


    def update_metadata(self, new_metadata: SessionMetadata):
        data = new_metadata.model_dump_json(indent=2)
        self.metadata_file.write_text(data, encoding="utf-8")
        logger.info("[store.py] Metadata updated")


    def append_transcript(self, transcript_event: TranscriptEvent):
        data = transcript_event.model_dump_json()
        with self.transcript_file.open("a") as f:
            f.write(data)
            f.write("\n")
        logger.info("Transcript event appended.")

    def read_metadata(self):
        m = self.metadata_file.read_text(encoding="utf-8")
        m_j = json.loads(m)
        metadata = SessionMetadata.model_validate(m_j)
        return metadata

    def read_transcript_data(self):
        events = [
            TranscriptEvent.model_validate_json(line)
            for line in self.transcript_file.read_text().splitlines()
        ]
        transcript = SessionTranscript(events=events)
        return transcript

    def read_session_data(self):
        metadata = self.read_metadata()
        transcript = self.read_transcript_data()
        return SessionData(
            session_id=self.session_id,
            metadata=metadata,
            transcript=transcript
        )

    def close(self):
        metadata = self.read_metadata()
        metadata.ended_at = datetime.now(UTC)
        self.update_metadata(metadata)
