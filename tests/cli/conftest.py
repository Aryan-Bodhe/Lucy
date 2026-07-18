import pytest

from lucy.cli import auth, app, doctor, dispatcher


class DummyAgent:
    def __init__(self, *, model, callback_handler=None):
        self.model = model
        self.callback_handler = callback_handler
        self.calls = []

    def __call__(self, prompt):
        self.calls.append(prompt)
        return {"message": "ok"}


class DummyModel:
    def __init__(self, *, model_id, client_args):
        self.model_id = model_id
        self.client_args = client_args


class DummyAuthError(Exception):
    pass


@pytest.fixture(autouse=True)
def cli_test_defaults(monkeypatch):
    monkeypatch.setattr(auth, "Agent", DummyAgent)
    monkeypatch.setattr(auth, "OpenAIModel", DummyModel)
    monkeypatch.setattr(auth, "AuthenticationError", DummyAuthError)
    monkeypatch.setattr(doctor, "SUPPORTED_PROVIDERS", [("openai", "gpt-test")])
    monkeypatch.setattr(dispatcher, "run_app", lambda: None)
    monkeypatch.setattr(app, "run_agent", lambda prompt: ({"content": prompt, "metadata": {"usage": {"inputTokens": 1}}}, 1.0))
