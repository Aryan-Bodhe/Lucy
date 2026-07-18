import pytest

from lucy.agent import agent

from ._helpers import DummyAgent, DummyOpenAIModel


@pytest.fixture(autouse=True)
def reset_agent_state(monkeypatch):
    monkeypatch.setattr(agent, "_agent", None)
    monkeypatch.setattr(agent, "Agent", DummyAgent)
    monkeypatch.setattr(agent, "OpenAIModel", DummyOpenAIModel)
    monkeypatch.setattr(agent, "AgentSkills", lambda skills: {"skills": str(skills)})
    monkeypatch.setattr(agent, "ProgressHook", lambda: "progress-hook")
    monkeypatch.setattr(agent, "SensitiveToolApproval", lambda: "approval")
    monkeypatch.setattr(agent, "PROMPT", "system prompt")
    monkeypatch.setattr(agent, "get_prompt_metadata", lambda: " [meta]")
    monkeypatch.setattr(agent, "MODEL", "gpt-test")
    monkeypatch.setattr(agent, "SKILLS_DIR", "/skills")
    monkeypatch.setattr(agent, "APP_NAME", "lucy")
    monkeypatch.setattr(agent, "MODEL_PROVIDER", "openai")
