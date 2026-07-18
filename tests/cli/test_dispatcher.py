from argparse import Namespace

from lucy.cli import dispatcher


class DummyAuthUI:
    def __init__(self):
        self.login_called = False
        self.logout_called = False

    def render_login_flow(self):
        self.login_called = True

    def render_logout_flow(self):
        self.logout_called = True


class DummyDoctorUI:
    def __init__(self):
        self.doctor_called = False

    def render_doctor_flow(self):
        self.doctor_called = True


class DummyUI:
    def __init__(self):
        self.auth = DummyAuthUI()
        self.doctor = DummyDoctorUI()


def test_dispatch_command_routes_login(monkeypatch):
    ui = DummyUI()
    run_app_called = []
    monkeypatch.setattr(dispatcher, "ui", ui)
    monkeypatch.setattr(dispatcher, "run_app", lambda: run_app_called.append(True))

    dispatcher.dispatch_command(Namespace(command="login"))

    assert ui.auth.login_called is True
    assert run_app_called == []


def test_dispatch_command_routes_logout(monkeypatch):
    ui = DummyUI()
    run_app_called = []
    monkeypatch.setattr(dispatcher, "ui", ui)
    monkeypatch.setattr(dispatcher, "run_app", lambda: run_app_called.append(True))

    dispatcher.dispatch_command(Namespace(command="logout"))

    assert ui.auth.logout_called is True
    assert run_app_called == []


def test_dispatch_command_routes_doctor(monkeypatch):
    ui = DummyUI()
    run_app_called = []
    monkeypatch.setattr(dispatcher, "ui", ui)
    monkeypatch.setattr(dispatcher, "run_app", lambda: run_app_called.append(True))

    dispatcher.dispatch_command(Namespace(command="doctor"))

    assert ui.doctor.doctor_called is True
    assert run_app_called == []


def test_dispatch_command_defaults_to_run_app(monkeypatch):
    ui = DummyUI()
    run_app_called = []
    monkeypatch.setattr(dispatcher, "ui", ui)
    monkeypatch.setattr(dispatcher, "run_app", lambda: run_app_called.append(True))

    dispatcher.dispatch_command(Namespace(command="unknown"))

    assert run_app_called == [True]
