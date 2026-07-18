import pytest

from lucy.cli import auth

from .conftest import DummyAgent, DummyAuthError


def test_get_api_key_delegates_to_keyring(monkeypatch):
    seen = {}

    def fake_get_password(app_name, provider):
        seen["args"] = (app_name, provider)
        return "secret"

    monkeypatch.setattr(auth.keyring, "get_password", fake_get_password)

    result = auth.get_api_key("openai")

    assert result == "secret"
    assert seen["args"] == (auth.APP_NAME, "openai")



def test_validate_api_key_returns_true_on_success(monkeypatch):
    logger_calls = []
    monkeypatch.setattr(auth.logger, "info", lambda msg: logger_calls.append(msg))

    assert auth.validate_api_key("sk-test", "openai", "gpt-test") is True
    assert logger_calls == ["API key validated for provider=openai"]


def test_validate_api_key_returns_false_on_authentication_error(monkeypatch):
    class FailingAgent(DummyAgent):
        def __call__(self, prompt):
            raise DummyAuthError()

    monkeypatch.setattr(auth, "Agent", FailingAgent)
    warnings = []
    monkeypatch.setattr(auth.logger, "warning", lambda msg: warnings.append(msg))

    assert auth.validate_api_key("sk-test", "openai", "gpt-test") is False
    assert warnings == ["Incorrect API key received for provider=openai"]


def test_validate_api_key_reraises_unexpected_errors(monkeypatch):
    class BrokenAgent(DummyAgent):
        def __call__(self, prompt):
            raise RuntimeError("boom")

    monkeypatch.setattr(auth, "Agent", BrokenAgent)

    with pytest.raises(RuntimeError, match="boom"):
        auth.validate_api_key("sk-test", "openai", "gpt-test")


def test_store_api_key_persists_key_when_valid(monkeypatch):
    set_calls = []
    monkeypatch.setattr(auth, "validate_api_key", lambda api_key, provider, model_id: True)
    monkeypatch.setattr(auth.keyring, "set_password", lambda app_name, provider, api_key: set_calls.append((app_name, provider, api_key)))
    infos = []
    monkeypatch.setattr(auth.logger, "info", lambda msg: infos.append(msg))

    assert auth.store_api_key("sk-test", provider="openai") is True
    assert set_calls == [(auth.APP_NAME, "openai", "sk-test")]
    assert infos == ["API key stored in keyring for provider=openai"]


def test_store_api_key_returns_false_when_invalid(monkeypatch):
    monkeypatch.setattr(auth, "validate_api_key", lambda api_key, provider, model_id: False)
    monkeypatch.setattr(auth.keyring, "set_password", lambda *args, **kwargs: pytest.fail("should not store"))

    assert auth.store_api_key("sk-test", provider="openai") is False


def test_delete_api_key_returns_false_when_missing(monkeypatch):
    monkeypatch.setattr(auth, "get_api_key", lambda provider: None)
    monkeypatch.setattr(auth.keyring, "delete_password", lambda *args, **kwargs: pytest.fail("should not delete"))

    assert auth.delete_api_key("openai") is False


def test_delete_api_key_removes_existing_key(monkeypatch):
    delete_calls = []
    monkeypatch.setattr(auth, "get_api_key", lambda provider: "secret")
    monkeypatch.setattr(auth.keyring, "delete_password", lambda app_name, provider: delete_calls.append((app_name, provider)))
    infos = []
    monkeypatch.setattr(auth.logger, "info", lambda msg: infos.append(msg))

    assert auth.delete_api_key("openai") is True
    assert delete_calls == [(auth.APP_NAME, "openai")]
    assert infos == ["API Key deleted for provider=openai"]
