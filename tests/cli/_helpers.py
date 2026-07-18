from types import SimpleNamespace


class DummyRequest:
    def __init__(self, prompt="hello"):
        self.prompt = prompt
        self.usage = None
        self.time_elapsed = None
        self.print_called = False

    def input(self):
        return self.prompt

    def print(self, *args, **kwargs):
        self.print_called = True


class DummyLifecycle:
    def __init__(self, request):
        self.request = request

    def __enter__(self):
        return self.request

    def __exit__(self, exc_type, exc, tb):
        return False


class DummyContext:
    def __init__(self, request=None):
        self.request = request or DummyRequest()
        self.initialise_called = False
        self.banner_render_called = False
        self.terminate_calls = []
        self.render_response_calls = []
        self.render_error_calls = []
        self.render_lifecycle_calls = 0
        self.responses = SimpleNamespace(
            render_response=lambda content: self.render_response_calls.append(content),
            render_error=lambda msg: self.render_error_calls.append(msg),
        )
        self.banner = SimpleNamespace(render=self._banner_render)

    def _banner_render(self):
        self.banner_render_called = True

    def initialise(self):
        self.initialise_called = True

    def terminate(self, clear_terminal):
        self.terminate_calls.append(clear_terminal)

    def render_request_lifecycle(self):
        self.render_lifecycle_calls += 1
        return DummyLifecycle(self.request)


class SessionManager:
    def __init__(self):
        self.entered = False
        self.exited = False

    def __enter__(self):
        self.entered = True
        return self

    def __exit__(self, exc_type, exc, tb):
        self.exited = True
        return False
