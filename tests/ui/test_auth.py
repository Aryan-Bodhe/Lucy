from types import SimpleNamespace

from lucy.ui import auth


class DummyConsole:
    def __init__(self):
        self.print_calls = []

    def print(self, *args, **kwargs):
        self.print_calls.append((args, kwargs))


def test_render_logout_flow_when_no_key(monkeypatch):
    console = DummyConsole()
    ui = auth.AuthUI(console)
    monkeypatch.setattr(auth.keyring, "get_password", lambda app_name, provider: None)
    monkeypatch.setattr(auth, "Panel", SimpleNamespace(fit=lambda msg, **kwargs: msg))

    ui.render_logout_flow()

    assert any("already logged out" in str(args[0]) for args, _ in console.print_calls if args)


def test_render_logout_flow_deletes_existing_key(monkeypatch):
    console = DummyConsole()
    ui = auth.AuthUI(console)
    deleted = []
    monkeypatch.setattr(auth.keyring, "get_password", lambda app_name, provider: "sk-test")
    monkeypatch.setattr(auth.keyring, "delete_password", lambda app_name, provider: deleted.append((app_name, provider)))
    monkeypatch.setattr(auth, "Panel", SimpleNamespace(fit=lambda msg, **kwargs: msg))

    ui.render_logout_flow()

    assert deleted == [(auth.APP_NAME, auth.MODEL_PROVIDER)]
    assert any("Successfully logged out" in str(args[0]) for args, _ in console.print_calls if args)
