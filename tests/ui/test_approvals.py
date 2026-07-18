from types import SimpleNamespace

from lucy.ui import approvals


class DummyConsole:
    def __init__(self, input_value=""):
        self.input_value = input_value
        self.print_calls = []
        self.input_calls = []

    def print(self, *args, **kwargs):
        self.print_calls.append((args, kwargs))

    def input(self, prompt, password=False):
        self.input_calls.append((prompt, password))
        return self.input_value


class DummyLive:
    def __init__(self, panel, transient=False):
        self.panel = panel
        self.transient = transient
        self.updated = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def update(self, value):
        self.updated.append(value)


def test_check_approval_accepts_empty_and_yes_values():
    assert approvals._check_approval("") is True
    assert approvals._check_approval(" y ") is True
    assert approvals._check_approval("YES") is True
    assert approvals._check_approval("ok") is True
    assert approvals._check_approval("no") is False


def test_render_sudo_permission_request_prompts_for_password(monkeypatch):
    console = DummyConsole(input_value="secret")
    monkeypatch.setattr(approvals, "Panel", SimpleNamespace(fit=lambda msg, style=None: (msg, style)))
    monkeypatch.setattr(approvals, "WARNING", "yellow")

    ui = approvals.ApprovalUI(console)
    result = ui.render_sudo_permission_request("shell", "sudo apt update")

    assert result == "secret"
    assert console.input_calls == [("Password > ", True)]
    assert console.print_calls or console.input_calls


def test_render_approval_returns_true_for_approved_input(monkeypatch):
    console = DummyConsole(input_value="")
    live = DummyLive(None, transient=True)
    monkeypatch.setattr(approvals, "Panel", SimpleNamespace(fit=lambda msg, style=None: (msg, style)))
    monkeypatch.setattr(approvals, "Live", lambda panel, transient=False: live)
    monkeypatch.setattr(approvals, "Text", lambda value: value)
    monkeypatch.setattr(approvals, "WARNING", "yellow")

    ui = approvals.ApprovalUI(console)
    result = ui.render_approval("editor", "view file.py")

    assert result is True
    assert console.input_calls == [("> Press Enter to approve, type no to deny. ", False)]
    assert live.updated == [""]


def test_render_approval_returns_false_for_denied_input(monkeypatch):
    console = DummyConsole(input_value="no")
    live = DummyLive(None, transient=True)
    monkeypatch.setattr(approvals, "Panel", SimpleNamespace(fit=lambda msg, style=None: (msg, style)))
    monkeypatch.setattr(approvals, "Live", lambda panel, transient=False: live)
    monkeypatch.setattr(approvals, "Text", lambda value: value)
    monkeypatch.setattr(approvals, "WARNING", "yellow")

    ui = approvals.ApprovalUI(console)
    result = ui.render_approval("editor", "view file.py")

    assert result is False


def test_render_approval_uses_fallback_message_on_format_error(monkeypatch):
    console = DummyConsole(input_value="")
    live = DummyLive(None, transient=True)

    class BadTemplate:
        def format(self, *args, **kwargs):
            raise ValueError("boom")

    monkeypatch.setattr(approvals, "TOOL_TEXT", BadTemplate())
    monkeypatch.setattr(approvals, "Panel", SimpleNamespace(fit=lambda msg, style=None: (msg, style)))
    monkeypatch.setattr(approvals, "Live", lambda panel, transient=False: live)
    monkeypatch.setattr(approvals, "Text", lambda value: value)
    monkeypatch.setattr(approvals, "WARNING", "yellow")

    ui = approvals.ApprovalUI(console)
    result = ui.render_approval("editor", "view file.py")

    assert result is True
    assert console.print_calls or console.input_calls
