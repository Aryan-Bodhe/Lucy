import lucy.ui.doctor as ui_doctor
import lucy.cli.doctor as cli_doctor


class DummyConsole:
    def __init__(self):
        self.print_calls = []
        self.rule_calls = []

    def print(self, *args, **kwargs):
        self.print_calls.append((args, kwargs))

    def rule(self, *args, **kwargs):
        self.rule_calls.append((args, kwargs))


class DummyEvent:
    def __init__(self, name, status, details, fix=None):
        self.name = name
        self.status = status
        self.details = details
        self.fix = fix


def test_render_doctor_flow_renders_summary_and_statuses(monkeypatch):
    console = DummyConsole()
    ui = ui_doctor.DoctorUI(console)
    events = [
        DummyEvent("Git", "passed", "/usr/bin/git"),
        DummyEvent("Internet", "warning", "Offline", "Connect to the internet."),
        DummyEvent("Logs", "failed", "/tmp/logs", "Directory is not writable."),
        DummyEvent("Path", "skipped", "Not checked"),
    ]

    monkeypatch.setattr(cli_doctor, "run_doctor", lambda: events, raising=False)

    ui.render_doctor_flow()

    assert console.rule_calls
    printed = "\n".join(str(args[0]) for args, _ in console.print_calls if args)
    assert "Lucy is not ready to use." in printed
    assert "Doctor ran 4 health checks" in printed
    assert any("Passed:" in str(args[0]) for args, _ in console.print_calls if args)
    assert any("Passed:" in str(args[0]) for args, _ in console.print_calls if args)


def test_render_doctor_flow_ready_message_changes_with_results(monkeypatch):
    console = DummyConsole()
    ui = ui_doctor.DoctorUI(console)

    monkeypatch.setattr(
        cli_doctor,
        "run_doctor",
        lambda: [DummyEvent("Git", "passed", "/usr/bin/git")],
    )

    ui.render_doctor_flow()

    assert any(
        "Lucy is ready to use!" in str(args[0])
        for args, _ in console.print_calls
        if args
    )
