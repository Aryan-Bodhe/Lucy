from contextlib import contextmanager
from types import SimpleNamespace


class FakeUI:
    """Stands in for `lucy.ui.core.ui`; records what the CLI asked it to render."""

    def __init__(self, prompts=("hello",)):
        self._prompts = list(prompts)
        self.responses_rendered = []
        self.errors_rendered = []
        self.rules = []
        self.terminate_calls = []
        self.initialise_called = False
        self.banner_render_called = False
        self.responses = SimpleNamespace(
            render_response=self.responses_rendered.append,
            render_error=self.errors_rendered.append,
        )
        self.banner = SimpleNamespace(render=self._render_banner)

    def _render_banner(self):
        self.banner_render_called = True

    def input(self):
        prompt = self._prompts.pop(0)
        if isinstance(prompt, BaseException):
            raise prompt
        return prompt

    def print(self, msg=""):
        pass

    def rule(self, title):
        self.rules.append(title)

    def initialise(self):
        self.initialise_called = True

    def terminate(self, clear_terminal=False):
        self.terminate_calls.append(clear_terminal)


class FakeSessionManager:
    def __init__(self):
        self.transcript = []
        self.metadata_updates = []
        self.session_entered = False
        self.session_exited = False
        self.request_scopes = 0

    def append_transcript(self, role, message):
        self.transcript.append((role, message))

    def update_metadata(self, model_id, usage):
        self.metadata_updates.append((model_id, usage))

    @contextmanager
    def session_scope(self):
        self.session_entered = True
        try:
            yield
        finally:
            self.session_exited = True

    @contextmanager
    def request_scope(self):
        self.request_scopes += 1
        yield


def fake_agent_result(text="hello world", usage=None, context_size=4_000):
    """Mimics the parts of strands.agent.AgentResult that the CLI reads."""
    usage = usage or {"inputTokens": 1_000, "outputTokens": 100, "totalTokens": 1_100}
    return SimpleNamespace(
        message={"content": [{"text": text}]},
        metrics=SimpleNamespace(
            latest_agent_invocation=SimpleNamespace(usage=usage),
            latest_context_size=context_size,
            # Lifetime totals of the cached agent: must never be what gets saved.
            accumulated_usage={"inputTokens": 999_999, "outputTokens": 999_999, "totalTokens": 1_999_998},
        ),
    )
