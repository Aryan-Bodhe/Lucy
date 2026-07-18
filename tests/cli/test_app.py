from types import SimpleNamespace

import pytest

from lucy.cli import app

from ._helpers import DummyContext, DummyRequest, SessionManager


def test_handle_request_success(monkeypatch):
    captured = {}

    def fake_run_agent(prompt):
        captured["prompt"] = prompt
        return (
            {"content": [{"text": "hello world"}], "metadata": {"usage": {"inputTokens": 1}}},
            1.25,
        )

    token_calls = []

    class TokenCtx:
        def __enter__(self):
            token_calls.append("enter")

        def __exit__(self, exc_type, exc, tb):
            token_calls.append("exit")
            return False

    monkeypatch.setattr(app, "run_agent", fake_run_agent)
    monkeypatch.setattr(app, "token_manager", lambda: TokenCtx())

    result = app.handle_request("prompt text")

    assert captured["prompt"] == "prompt text"
    assert token_calls == ["enter", "exit"]
    assert result.content == "hello world"
    assert result.usage == {"inputTokens": 1}
    assert result.time == 1.25


from unittest.mock import Mock

@pytest.mark.parametrize(
    "exc,message",
    [
        (
            app.NotFoundError(
                "not found",
                response=Mock(),
                body={},
            ),
            "Selected model is not available. Please check model ID and try again.",
        ),
        (
            app.RateLimitError(
                "rate limit",
                response=Mock(),
                body={},
            ),
            "You have exhausted your token credits for selected model. Please check your API balance and try again.",
        ),
        (
            app.APIConnectionError(
                request=Mock(),
            ),
            "Unable to connect to servers. Please check your internet connection and try again.",
        ),
        # ...
    ],
)
def test_handle_request_renders_expected_errors(monkeypatch, exc, message):
    monkeypatch.setattr(
        app,
        "run_agent",
        lambda prompt: (_ for _ in ()).throw(exc),
    )


def test_handle_request_renders_generic_error_and_logs(monkeypatch):
    monkeypatch.setattr(app, "run_agent", lambda prompt: (_ for _ in ()).throw(RuntimeError("boom")))
    errors = []
    logged = []
    monkeypatch.setattr(app.ui.responses, "render_error", lambda msg: errors.append(msg))
    monkeypatch.setattr(app.logger, "exception", lambda msg: logged.append(msg))

    assert app.handle_request("prompt") is None
    assert errors == ["An unexpected error occurred. Please restart the app and try again."]
    assert logged == ["Unhandled exception"]


def test_run_app_happy_path(monkeypatch):
    ctx = DummyContext(DummyRequest(prompt="first prompt"))
    session_mgr = SessionManager()
    responses = []

    monkeypatch.setattr(app, "ui", ctx)
    monkeypatch.setattr(app, "session_manager", lambda: session_mgr)
    monkeypatch.setattr(app, "handle_request", lambda prompt: SimpleNamespace(content="response", usage={"u": 1}, time=2.5))
    monkeypatch.setattr(app, "CLEAR_TERMINAL_UPON_EXIT", False)

    def render_response(content):
        responses.append(content)
        raise StopIteration

    monkeypatch.setattr(ctx.responses, "render_response", render_response)

    with pytest.raises(StopIteration):
        app.run_app()

    assert ctx.initialise_called is True
    assert ctx.banner_render_called is True
    assert session_mgr.entered is True
    assert ctx.request.usage == {"u": 1}
    assert ctx.request.time_elapsed == 2.5
    assert ctx.request.print_called is True
    assert responses == ["response"]
