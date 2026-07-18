import pytest

from lucy.agent import agent

from ._helpers import DummyAgent, DummyOpenAIModel, DummyRetryStrategy


def test_init_model_returns_openai_model_when_key_exists(monkeypatch):
    monkeypatch.setattr(agent.keyring, "get_password", lambda app_name, provider: "sk-test")

    model = agent._init_model()

    assert isinstance(model, DummyOpenAIModel)
    assert model.kwargs == {"model_id": "gpt-test", "client_args": {"api_key": "sk-test"}}


def test_init_model_raises_when_key_missing(monkeypatch):
    monkeypatch.setattr(agent.keyring, "get_password", lambda app_name, provider: None)
    errors = []
    monkeypatch.setattr(agent.logger, "error", lambda msg: errors.append(msg))

    with pytest.raises(ValueError, match="OpenAI API key not set."):
        agent._init_model()

    assert errors == ["OpenAI API key not set."]


def test_get_or_create_agent_reuses_existing_instance(monkeypatch):
    existing = DummyAgent()
    monkeypatch.setattr(agent, "_agent", existing)

    result = agent._get_or_create_agent()

    assert result is existing


def test_get_or_create_agent_builds_agent(monkeypatch):
    monkeypatch.setattr(agent.keyring, "get_password", lambda app_name, provider: "sk-test")
    infos = []
    monkeypatch.setattr(agent.logger, "info", lambda msg, *args: infos.append(msg % args if args else msg))
    monkeypatch.setattr(agent, "ModelRetryStrategy", DummyRetryStrategy)

    result = agent._get_or_create_agent()

    assert isinstance(result, DummyAgent)
    assert result.kwargs["system_prompt"] == "system prompt"
    assert result.kwargs["tools"] is agent.ALL_TOOLS
    assert result.kwargs["plugins"]
    assert result.kwargs["hooks"] == ["progress-hook"]
    assert result.kwargs["interventions"] == ["approval"]
    assert result.kwargs["retry_strategy"].max_attempts == 3
    assert infos[0] == "Initializing Strands Agent."
    assert infos[1] == "OpenAI model instance created successfully."
    assert infos[2] == "Created Agent instance successfully."


def test_run_agent_appends_metadata_and_returns_message(monkeypatch):
    monkeypatch.setattr(agent.keyring, "get_password", lambda app_name, provider: "sk-test")
    fake_agent = DummyAgent()
    monkeypatch.setattr(agent, "_agent", fake_agent)
    times = iter([10.0, 11.25])
    monkeypatch.setattr(agent.time, "perf_counter", lambda: next(times))

    logs = []
    monkeypatch.setattr(agent.logger, "info", lambda msg, *args: logs.append(msg % args if args else msg))

    message, elapsed = agent.run_agent("hello")

    assert fake_agent.calls == ["hello [meta]"]
    assert message == {"content": "hello [meta]"}
    assert elapsed == 1.25
    assert any("token_usage=1/2/0/0 resp_time=1.25s" in entry for entry in logs)
