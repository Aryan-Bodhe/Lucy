from lucy.ui import tools


class DummyConsole:
    def __init__(self):
        self.print_calls = []

    def print(self, *args, **kwargs):
        self.print_calls.append((args, kwargs))


def test_render_status_running_tool(monkeypatch):
    console = DummyConsole()
    ui = tools.ToolUI(console)

    ui.render_status("editor", "view file.py", status="running", tool_type="tool")

    assert console.print_calls[0] == ((), {})
    assert "Running tool" in console.print_calls[1][0][0]
    assert "editor" in console.print_calls[1][0][0]
    assert "view file.py" in console.print_calls[2][0][0]


def test_render_status_failed_skill(monkeypatch):
    console = DummyConsole()
    ui = tools.ToolUI(console)

    ui.render_status("system-operations", "ignored", status="failed", tool_type="skill")

    assert console.print_calls[0] == ((), {})
    assert "Error reading skill" in console.print_calls[1][0][0]
    assert "system-operations" in console.print_calls[1][0][0]
    assert len(console.print_calls) == 2


def test_render_status_success_tool(monkeypatch):
    console = DummyConsole()
    ui = tools.ToolUI(console)

    ui.render_status("shell", "ls -la", status="success", tool_type="tool")

    assert console.print_calls[0] == ((), {})
    assert "Finished running tool" in console.print_calls[1][0][0]
    assert "shell" in console.print_calls[1][0][0]
    assert console.print_calls[2][0][0] == "   ∟ ls -la"


def test_render_status_refused_tool(monkeypatch):
    console = DummyConsole()
    ui = tools.ToolUI(console)

    ui.render_status("editor", "view file.py", status="refused", tool_type="tool")

    assert console.print_calls[0] == ((), {})
    assert "User denied tool" in console.print_calls[1][0][0]
    assert "editor" in console.print_calls[1][0][0]
    assert console.print_calls[2][0][0] == "   ∟ view file.py"
