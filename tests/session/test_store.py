from pathlib import Path

import pytest

from lucy.session.models import SessionData, SessionTranscript, TranscriptEvent


def test_initialise_creates_directory_and_files(sessions_dir, session_id):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id)
    returned = store.initialise()

    assert returned is store
    assert store.path.exists()
    assert store.path.is_dir()
    assert store.metadata_file.exists()
    assert store.transcript_file.exists()


def test_update_metadata_writes_json_and_read_metadata_round_trips(
    sessions_dir, session_id, sample_metadata
):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id).initialise()
    store.update_metadata(sample_metadata)

    loaded = store.read_metadata()
    assert loaded == sample_metadata
    assert loaded.model_dump() == sample_metadata.model_dump()


def test_append_transcript_appends_jsonl_lines(sessions_dir, session_id, sample_event):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id).initialise()

    second_event = sample_event.model_copy(update={"message": "second"})
    store.append_transcript(sample_event)
    store.append_transcript(second_event)

    text = store.transcript_file.read_text(encoding="utf-8").splitlines()
    assert len(text) == 2
    assert '"message":"hello"' in text[0] or '"message": "hello"' in text[0]
    assert '"message":"second"' in text[1] or '"message": "second"' in text[1]


def test_read_transcript_data_round_trips_multiple_events(sessions_dir, session_id, sample_event):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id).initialise()
    second_event = sample_event.model_copy(update={"message": "second"})
    store.append_transcript(sample_event)
    store.append_transcript(second_event)

    transcript = store.read_transcript_data()

    assert isinstance(transcript, SessionTranscript)
    assert transcript.events == [sample_event, second_event]


def test_read_session_data_combines_metadata_and_transcript(
    sessions_dir, session_id, sample_metadata, sample_event
):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id).initialise()
    store.update_metadata(sample_metadata)
    store.append_transcript(sample_event)

    session_data = store.read_session_data()

    assert isinstance(session_data, SessionData)
    assert session_data.session_id == session_id
    assert session_data.metadata == sample_metadata
    assert session_data.transcript.events == [sample_event]


def test_read_metadata_on_missing_file_raises(tmp_path, monkeypatch, session_id):
    from lucy.session import store as store_module
    from lucy.session.store import SessionStore

    monkeypatch.setattr(store_module, "SESSIONS_DIR", tmp_path / "sessions")
    store = SessionStore(session_id)
    with pytest.raises(FileNotFoundError):
        store.read_metadata()


def test_new_store_starts_untitled_and_title_round_trips(sessions_dir, session_id):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id).initialise()
    assert store.is_titled() is False

    metadata = store.read_metadata()
    metadata.session_title = "Fix Login Bug"
    store.update_metadata(metadata)

    assert store.is_titled() is True
    assert SessionStore(session_id).read_metadata().session_title == "Fix Login Bug"


def test_metadata_saved_before_titles_existed_still_loads(sessions_dir, session_id):
    from lucy.session.store import SessionStore

    store = SessionStore(session_id)
    store.path.mkdir(parents=True)
    store.metadata_file.write_text(
        '{"started_at": "2026-07-29T11:36:00Z", "ended_at": null, "usage": {}}',
        encoding="utf-8",
    )

    assert store.read_metadata().session_title is None
    assert store.is_titled() is False
