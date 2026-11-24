from unittest.mock import Mock

import pytest

from lucy.cli import app
from ._helpers import FakeSessionManager, FakeUI, fake_agent_result


@pytest.fixture()
def fake_ui(monkeypatch):
    ui = FakeUI()
    monkeypatch.setattr(app, "ui", ui)
    return ui


@pytest.fixture(autouse=True)
def fake_generate_title(monkeypatch):
    """Keep handle_request tests off the real title model."""
    calls = []

    def generate_title(prompt):
        calls.append(prompt)
        return "Generated Title"

    monkeypatch.setattr(app, "generate_title", generate_title)
    return calls


# ---------- _handle_request ----------

def test_handle_request_helper_returns_answer_usage_and_time(monkeypatch, fake_ui):
    captured = {}

    def fake_run_agent(prompt):
        captured["prompt"] = prompt
        return fake_agent_result(text="hello world"), 1.25

    monkeypatch.setattr(app, "run_agent", fake_run_agent)

    result = app._handle_request("prompt text")

    assert captured["prompt"] == "prompt text"
    assert result.content == "hello world"
    assert result.usage.input_tokens == 1_000
    assert result.time == 1.25


@pytest.mark.parametrize(
    "exc, message",
    [
        (
            app.NotFoundError("not found", response=Mock(), body={}),
            "Selected model is not available. Please check model ID and try again.",
        ),
        (
            app.RateLimitError("rate limit", response=Mock(), body={}),
            "You have exhausted your token credits for selected model. Please check your API balance and try again.",
        ),
        (
            app.APIConnectionError(request=Mock()),
            "Unable to connect to servers. Please check your internet connection and try again.",
        ),
        (
            app.AuthenticationError("bad key", response=Mock(), body={}),
            "Your API key is missing or invalid. Please run 'lucy login' in your terminal to set one.",
        ),
        (
            ValueError("OpenAI API key not set."),
            "Your API key is missing or invalid. Please run 'lucy login' in your terminal to set one.",
        ),
        (
            RuntimeError("boom"),
            "An unexpected error occurred. Please restart the app and try again.",
        ),
    ],
    ids=["model_not_found", "insufficient_credits", "connection_error", "auth_error", "missing_key", "unexpected"],
)
def test_handle_request_helper_renders_error_and_returns_none(monkeypatch, fake_ui, exc, message):
    def failing_run_agent(prompt):
        raise exc

    monkeypatch.setattr(app, "run_agent", failing_run_agent)

    assert app._handle_request("prompt") is None
    assert fake_ui.errors_rendered == [message]


def test_handle_request_helper_logs_unexpected_errors(monkeypatch, fake_ui):
    logged = []
    monkeypatch.setattr(app, "run_agent", Mock(side_effect=RuntimeError("boom")))
    monkeypatch.setattr(app.logger, "exception", lambda msg: logged.append(msg))

    app._handle_request("prompt")

    assert logged == ["Unhandled exception"]


# ---------- handle_request ----------

def test_handle_request_records_turn_and_renders_answer(monkeypatch, fake_ui):
    session = FakeSessionManager()
    monkeypatch.setattr(app, "run_agent", lambda prompt: (fake_agent_result(text="hi there"), 2.0))

    app.handle_request(session)

    assert session.transcript == [("user", "hello"), ("agent", "hi there")]
    assert session.request_scopes == 1
    (model_id, usage), = session.metadata_updates
    assert model_id == app.MODEL
    assert usage.input_tokens == 1_000  # this turn's usage, not the agent's lifetime total
    assert fake_ui.responses_rendered == ["hi there"]
    assert len(fake_ui.rules) == 1


def test_handle_request_survives_failed_agent_call(monkeypatch, fake_ui):
    session = FakeSessionManager()
    monkeypatch.setattr(app, "run_agent", Mock(side_effect=app.RateLimitError("rate limit", response=Mock(), body={})))

    app.handle_request(session)  # must not raise: the session should keep running

    assert session.transcript == [("user", "hello")]
    assert session.metadata_updates == []
    assert fake_ui.responses_rendered == []
    assert len(fake_ui.errors_rendered) == 1


def test_handle_request_terminates_on_ctrl_c(monkeypatch):
    ui = FakeUI(prompts=[KeyboardInterrupt()])
    monkeypatch.setattr(app, "ui", ui)
    session = FakeSessionManager()

    with pytest.raises(KeyboardInterrupt):
        app.handle_request(session)

    assert ui.terminate_calls == [app.CLEAR_TERMINAL_UPON_EXIT]
    assert session.transcript == []


# ---------- session titles ----------

def test_handle_request_titles_untitled_session_from_first_prompt(monkeypatch, fake_ui, fake_generate_title):
    session = FakeSessionManager()
    monkeypatch.setattr(app, "run_agent", lambda prompt: (fake_agent_result(text="hi"), 1.0))

    app.handle_request(session)

    assert fake_generate_title == ["hello"]
    assert session.title_updates == ["Generated Title"]


def test_handle_request_does_not_retitle_titled_session(monkeypatch, fake_ui, fake_generate_title):
    session = FakeSessionManager()
    session.title = "Existing"
    monkeypatch.setattr(app, "run_agent", lambda prompt: (fake_agent_result(text="hi"), 1.0))

    app.handle_request(session)

    assert fake_generate_title == []
    assert session.title_updates == []


def test_handle_request_falls_back_to_prompt_when_title_generation_fails(monkeypatch):
    ui = FakeUI(prompts=["  Fix the login bug\nand add tests"])
    monkeypatch.setattr(app, "ui", ui)
    monkeypatch.setattr(app, "generate_title", lambda prompt: None)
    monkeypatch.setattr(app, "run_agent", lambda prompt: (fake_agent_result(text="ok"), 1.0))
    session = FakeSessionManager()

    app.handle_request(session)

    assert session.title_updates == ["Fix the login bug"]
    assert ui.responses_rendered == ["ok"]  # the turn still completes


@pytest.mark.parametrize("prompt", ["", "   ", "\n\n"])
def test_handle_request_skips_title_for_blank_prompt(monkeypatch, fake_generate_title, prompt):
    ui = FakeUI(prompts=[prompt])
    monkeypatch.setattr(app, "ui", ui)
    monkeypatch.setattr(app, "run_agent", lambda prompt: (fake_agent_result(text="ok"), 1.0))
    session = FakeSessionManager()

    app.handle_request(session)  # must not raise

    assert fake_generate_title == []
    assert session.title_updates == []


# ---------- run_app ----------

def test_run_app_loops_until_interrupted_and_closes_session(monkeypatch, fake_ui):
    session = FakeSessionManager()
    monkeypatch.setattr(app, "SessionManager", lambda: session)
    handle = Mock(side_effect=[None, None, KeyboardInterrupt()])
    monkeypatch.setattr(app, "handle_request", handle)

    with pytest.raises(KeyboardInterrupt):
        app.run_app()

    assert handle.call_count == 3
    handle.assert_called_with(session)
    assert fake_ui.initialise_called is True
    assert fake_ui.banner_render_called is True
    assert session.session_entered is True
    assert session.session_exited is True
