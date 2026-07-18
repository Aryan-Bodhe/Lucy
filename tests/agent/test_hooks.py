from types import SimpleNamespace

from lucy.agent import hooks


class DummyRegistry:
    def __init__(self):
        self.callbacks = []

    def add_callback(self, event_type, callback):
        self.callbacks.append((event_type, callback))


class DummyResult(dict):
    pass


class DummyEvent:
    def __init__(self, name, input_data, result=None, exception=None, cancel_message=None):
        self.tool_use = {"name": name, "input": input_data}
        self.result = result if result is not None else {}
        self.exception = exception
        self.cancel_message = cancel_message


def test_register_hooks_adds_callbacks(monkeypatch):
    registry = DummyRegistry()
    hook = hooks.ProgressHook()

    hook.register_hooks(registry)

    assert registry.callbacks == [
        (hooks.BeforeToolCallEvent, hook.before_tool),
        (hooks.AfterToolCallEvent, hook.after_tool),
    ]


def test_before_tool_renders_running_status(monkeypatch):
    rendered = []
    monkeypatch.setattr(hooks, "parse_tool_parameters", lambda name, input_data: f"parsed:{name}")
    monkeypatch.setattr(hooks.logger, "info", lambda msg, *args: rendered.append(msg % args if args else msg))
    monkeypatch.setattr(hooks.ui.tools, "render_status", lambda *args, **kwargs: rendered.append((args, kwargs)))

    hooks.ProgressHook().before_tool(DummyEvent("editor", {"command": "view"}))

    assert rendered[0] == "Calling tool=editor input={'command': 'view'}"
    assert rendered[1][0][0] == "editor"
    assert rendered[1][1]["tool_command"] == "parsed:editor"
    assert rendered[1][1]["tool_type"] == "tool"
    assert rendered[1][1]["status"] == "running"


def test_before_tool_uses_command_for_skills(monkeypatch):
    calls = []
    monkeypatch.setattr(hooks, "parse_tool_parameters", lambda name, input_data: "system-operations")
    monkeypatch.setattr(hooks.logger, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(hooks.ui.tools, "render_status", lambda *args, **kwargs: calls.append((args, kwargs)))

    hooks.ProgressHook().before_tool(DummyEvent("skills", {"skill_name": "system-operations"}))

    assert calls[0][0][0] == "system-operations"
    assert calls[0][1]["tool_type"] == "skill"


def test_after_tool_success(monkeypatch):
    logs = []
    rendered = []
    monkeypatch.setattr(hooks, "parse_tool_parameters", lambda name, input_data: "parsed-cmd")
    monkeypatch.setattr(hooks.logger, "info", lambda msg, *args: logs.append(msg % args if args else msg))
    monkeypatch.setattr(hooks.ui.tools, "render_status", lambda *args, **kwargs: rendered.append((args, kwargs)))

    hooks.ProgressHook().after_tool(DummyEvent("shell", {"command": "echo hi"}, result={"status": "ok"}))

    assert logs[-1] == "Tool succeeded: shell parsed-cmd"
    assert rendered[0][1]["status"] == "success"


def test_after_tool_failure_due_to_exception(monkeypatch):
    warnings = []
    rendered = []
    monkeypatch.setattr(hooks, "parse_tool_parameters", lambda name, input_data: "parsed-cmd")
    monkeypatch.setattr(hooks.logger, "error", lambda msg, *args, **kwargs: warnings.append(msg % args if args else msg))
    monkeypatch.setattr(hooks.ui.tools, "render_status", lambda *args, **kwargs: rendered.append((args, kwargs)))

    hooks.ProgressHook().after_tool(DummyEvent("editor", {"command": "view"}, exception=RuntimeError("boom")))

    assert warnings == ["Tool failed: editor parsed-cmd"]
    assert rendered[0][1]["status"] == "failed"


def test_after_tool_failure_due_to_result_error(monkeypatch):
    warnings = []
    rendered = []
    monkeypatch.setattr(hooks, "parse_tool_parameters", lambda name, input_data: "parsed-cmd")
    monkeypatch.setattr(hooks.logger, "warning", lambda msg, *args: warnings.append(msg % args if args else msg))
    monkeypatch.setattr(hooks.logger, "info", lambda *args, **kwargs: None)
    monkeypatch.setattr(hooks.ui.tools, "render_status", lambda *args, **kwargs: rendered.append((args, kwargs)))

    hooks.ProgressHook().after_tool(DummyEvent("editor", {"command": "view"}, result={"status": "error"}))

    assert warnings == ["Tool failed: editor parsed-cmd"]
    assert rendered[0][1]["status"] == "failed"


def test_after_tool_refused(monkeypatch):
    infos = []
    rendered = []
    monkeypatch.setattr(hooks, "parse_tool_parameters", lambda name, input_data: "parsed-cmd")
    monkeypatch.setattr(hooks.logger, "info", lambda msg, *args: infos.append(msg % args if args else msg))
    monkeypatch.setattr(hooks.ui.tools, "render_status", lambda *args, **kwargs: rendered.append((args, kwargs)))

    hooks.ProgressHook().after_tool(DummyEvent("editor", {"command": "view"}, cancel_message="nope"))

    assert infos[0] == "User refused tool: editor parsed-cmd"
    assert infos[-1] == "Tool succeeded: editor parsed-cmd"
    assert rendered[0][1]["status"] == "refused"
