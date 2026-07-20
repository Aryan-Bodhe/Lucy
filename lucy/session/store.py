import json
from pathlib import Path
from pydantic import ValidationError
from uuid import UUID

from lucy.session.models import SessionMetadata, SessionData, TranscriptEvent


class SessionStore:
    def __init__(
        self, 
        session_id: UUID, 
        session_dir: Path, 
        metadata_file: Path,
        transcript_file: Path
    ):
        self.session_id = session_id
        self.session_dir = session_dir
        self.metadata_file = metadata_file
        self.transcript_file = transcript_file


    def load(self):
        with self.metadata_file.open("r", encoding="utf-8") as f:
            metadata_dict = json.load(f)

        metadata = SessionMetadata.model_validate(metadata_dict)
        with self.transcript_file.open("r", encoding="utf-8") as f:
            transcript = [
                TranscriptEvent.model_validate_json(line)
                for line in f
            ]

        return SessionData(
            session_id=self.session_id, 
            metadata=metadata, 
            transcript=transcript
        )


    def append_transcript(self, event: TranscriptEvent) -> None:
        with self.transcript_file.open("a", encoding="utf-8") as f:
            f.write(f"{event.model_dump_json()}\n")


    def update_metadata(self, metadata: SessionMetadata):
        self.metadata_file.write_text(
            metadata.model_dump_json(indent=2),
            encoding="utf-8",
        )


    def validate(self) -> None:
        if not (
            self.metadata_file.exists()
            and self.transcript_file.exists()
        ):
            raise FileNotFoundError(
                f"Session {self.session_id} is corrupted."
            )

        try:
            with self.metadata_file.open("r", encoding="utf-8") as f:
                metadata = json.load(f)

            SessionMetadata.model_validate(metadata)

            with self.transcript_file.open("r", encoding="utf-8") as f:
                for line in f:
                    TranscriptEvent.model_validate_json(line)

        except (json.JSONDecodeError, ValidationError) as e:
            raise ValueError(
                f"Session {self.session_id} contains invalid data."
            ) from e
