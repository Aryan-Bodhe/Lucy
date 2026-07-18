from types import SimpleNamespace

from lucy import main


class DummyContext:
    def __init__(self):
        self.banner = SimpleNamespace(render=lambda: None)
        self.initialise_called = False
        self.terminate_calls = []
        self.auth = SimpleNamespace(render_login_flow=lambda: None, render_logout_flow=lambda: None)
        self.doctor = SimpleNamespace(render_doctor_flow=lambda: None)
        self.responses = SimpleNamespace(render_response=lambda content: None, render_error=lambda msg: None)

    def initialise(self):
        self.initialise_called = True

    def terminate(self, clear_terminal):
        self.terminate_calls.append(clear_terminal)


def test_main_dispatches_to_run_app(monkeypatch):
    called = []
    monkeypatch.setattr(main, "dispatch_command", lambda args: called.append(args.command))
    monkeypatch.setattr(main, "parse_args", lambda: SimpleNamespace(command=None))

    main.main()

    assert called == [None]


def test_main_initialises_ui_and_terminates(monkeypatch):
    ctx = DummyContext()
    monkeypatch.setattr(main, "ui", ctx)
    monkeypatch.setattr(main, "dispatch_command", lambda args: None)
    monkeypatch.setattr(main, "parse_args", lambda: SimpleNamespace(command=None))
    main.main()

    assert ctx.initialise_called is False
    assert ctx.terminate_calls == []


def test_main_passes_command_to_dispatcher(monkeypatch):
    seen = []
    monkeypatch.setattr(main, "dispatch_command", lambda args: seen.append(args.command))
    monkeypatch.setattr(main, "parse_args", lambda: SimpleNamespace(command="doctor"))
    monkeypatch.setattr(main, "ui", DummyContext())

    main.main()

    assert seen == ["doctor"]
