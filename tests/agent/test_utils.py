from datetime import datetime
from lucy.agent import utils

class MockDateTime:
    @classmethod
    def now(cls):
        return datetime(2026, 7, 18, 8, 29, 7)

    @classmethod
    def today(cls):
        return datetime(2026, 7, 18, 8, 29, 7)

class DummyCompletedProcess:
    def __init__(self, returncode=0):
        self.returncode = returncode


def test_parse_tool_parameters_for_editor_with_range():
    result = utils.parse_tool_parameters(
        "editor",
        {"command": "view", "path": "/tmp/file.py", "view_range": [1, 10]},
    )

    assert result == "view /tmp/file.py range=[1, 10]"


def test_parse_tool_parameters_for_shell():
    assert utils.parse_tool_parameters("shell", {"command": "ls -la"}) == "ls -la"


def test_parse_tool_parameters_for_handoff_to_user():
    assert utils.parse_tool_parameters("handoff_to_user", {}) is None


def test_parse_tool_parameters_for_skills():
    assert utils.parse_tool_parameters("skills", {"skill_name": "system-operations"}) == "system-operations"


def test_has_sudo_access_true(monkeypatch):
    monkeypatch.setattr(utils.subprocess, "run", lambda *args, **kwargs: DummyCompletedProcess(returncode=0))

    assert utils.has_sudo_access() is True


def test_has_sudo_access_false(monkeypatch):
    monkeypatch.setattr(utils.subprocess, "run", lambda *args, **kwargs: DummyCompletedProcess(returncode=1))

    assert utils.has_sudo_access() is False


def test_gain_sudo_privileges_returns_false_when_password_missing():
    assert utils.gain_sudo_privileges(None) is False


def test_gain_sudo_privileges_runs_sudo(monkeypatch):
    calls = []

    def fake_run(cmd, input=None, text=None, capture_output=None):
        calls.append((cmd, input, text, capture_output))
        return DummyCompletedProcess(returncode=0)

    monkeypatch.setattr(utils.subprocess, "run", fake_run)

    assert utils.gain_sudo_privileges("secret") is True
    assert calls[0][0] == ["sudo", "-S", "-p", "", "-v"]
    assert calls[0][1] == "secret\n"
    assert calls[0][2] is True
    assert calls[0][3] is True


def test_get_prompt_metadata_includes_expected_fields(monkeypatch):
    monkeypatch.setattr(utils.os, "getcwd", lambda: "/repo")
    monkeypatch.setattr(utils, "datetime", MockDateTime)

    result = utils.get_prompt_metadata()

    assert "Current repository root: /repo" in result
    assert "Current date: 2026-07-18 08:29:07" in result
