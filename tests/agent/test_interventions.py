import subprocess

from lucy.agent import interventions


class DummyApprovalUI:
    def __init__(self, approval_response=None, sudo_response=None):
        self.approval_response = approval_response
        self.sudo_response = sudo_response
        self.approvals = self
        self.calls = []

    def render_approval(self, tool_name, command):
        self.calls.append((tool_name, command, "approval"))
        return self.approval_response

    def render_sudo_permission_request(self, tool_name, command):
        self.calls.append((tool_name, command, "sudo"))
        return self.sudo_response


class DummyEvent:
    def __init__(self, name, input_data, result=None):
        self.tool_use = {"name": name, "input": input_data}
        self.result = result if result is not None else {}


class DummyCompletedProcess:
    def __init__(self, returncode=0):
        self.returncode = returncode


def test_sensitive_tool_approval_returns_confirm_for_sensitive_tool(monkeypatch):
    ui = DummyApprovalUI(approval_response=True)
    monkeypatch.setattr(interventions, "ui", ui)
    monkeypatch.setattr(interventions, "parse_tool_parameters", lambda name, input_data: "parsed-command")
    monkeypatch.setattr(interventions.logger, "info", lambda *args, **kwargs: None)

    result = interventions.SensitiveToolApproval().before_tool_call(DummyEvent("shell", {"command": "ls"}))

    assert result.__class__.__name__ == "Confirm"
    assert ui.calls == [("shell", "parsed-command", "approval")]


def test_sensitive_tool_approval_returns_proceed_for_safe_tool(monkeypatch):
    ui = DummyApprovalUI()
    monkeypatch.setattr(interventions, "ui", ui)

    result = interventions.SensitiveToolApproval().before_tool_call(DummyEvent("current_time", {}))

    assert result.__class__.__name__ == "Proceed"
    assert ui.calls == []


def test_has_sudo_access_detects_cached_credentials(monkeypatch):
    runs = []

    def fake_run(cmd, stdout=None, stderr=None):
        runs.append(cmd)
        return DummyCompletedProcess(returncode=0)

    monkeypatch.setattr(interventions.subprocess, "run", fake_run)

    assert interventions.SudoPasswordHandler()._has_sudo_access() is True
    assert runs == [["sudo", "-n", "true"]]


def test_gain_sudo_privileges_returns_false_when_password_missing(monkeypatch):
    monkeypatch.setattr(interventions, "subprocess", subprocess)

    handler = interventions.SudoPasswordHandler()
    assert handler._gain_sudo_privileges(None) is False


def test_gain_sudo_privileges_uses_sudo_password(monkeypatch):
    calls = []

    monkeypatch.setattr(interventions.SudoPasswordHandler, "_has_sudo_access", lambda self: False)

    def fake_run(cmd, input=None, text=None, capture_output=None):
        calls.append((cmd, input, text, capture_output))
        return DummyCompletedProcess(returncode=0)

    monkeypatch.setattr(interventions.subprocess, "run", fake_run)
    monkeypatch.setattr(interventions.logger, "info", lambda *args, **kwargs: None)

    handler = interventions.SudoPasswordHandler()
    assert handler._gain_sudo_privileges("secret") is True
    assert calls[0][0] == ["sudo", "-S", "-p", "", "-v"]
    assert calls[0][1] == "secret\n"


def test_after_tool_call_returns_proceed_when_no_error(monkeypatch):
    monkeypatch.setattr(interventions, "ui", DummyApprovalUI())

    result = interventions.SudoPasswordHandler().after_tool_call(DummyEvent("editor", {}, result={"status": "ok"}))

    assert result.__class__.__name__ == "Proceed"


def test_after_tool_call_requests_sudo_on_permission_denied(monkeypatch):
    ui = DummyApprovalUI(sudo_response="password")
    monkeypatch.setattr(interventions, "ui", ui)
    monkeypatch.setattr(interventions, "parse_tool_parameters", lambda name, input_data: "parsed-command")
    monkeypatch.setattr(interventions.SudoPasswordHandler, "_gain_sudo_privileges", lambda self, password: True)
    monkeypatch.setattr(interventions.logger, "info", lambda *args, **kwargs: None)

    event = DummyEvent("shell", {"command": "rm -rf /"}, result={"status": "error", "content": [{"text": "Permission denied"}]})
    result = interventions.SudoPasswordHandler().after_tool_call(event)

    assert result.__class__.__name__ == "Proceed"
    assert ui.calls == [("shell", "parsed-command", "sudo")]


def test_after_tool_call_denies_when_user_cancels_sudo(monkeypatch):
    ui = DummyApprovalUI(sudo_response=None)
    monkeypatch.setattr(interventions, "ui", ui)
    monkeypatch.setattr(interventions, "parse_tool_parameters", lambda name, input_data: "parsed-command")
    monkeypatch.setattr(interventions.SudoPasswordHandler, "_gain_sudo_privileges", lambda self, password: False)
    monkeypatch.setattr(interventions.logger, "info", lambda *args, **kwargs: None)

    event = DummyEvent("shell", {"command": "rm -rf /"}, result={"status": "error", "content": [{"text": "permission denied"}]})
    result = interventions.SudoPasswordHandler().after_tool_call(event)

    assert result.__class__.__name__ == "Deny"
    assert ui.calls == [("shell", "parsed-command", "sudo")]
