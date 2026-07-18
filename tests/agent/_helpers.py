class DummyMetrics:
    def __init__(self, usage):
        self.accumulated_usage = usage


class DummyResponse:
    def __init__(self, message="ok", usage=None):
        self.message = message
        self.metrics = DummyMetrics(usage or {"inputTokens": 1, "outputTokens": 2})


class DummyAgent:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.calls = []

    def __call__(self, prompt):
        self.calls.append(prompt)
        return DummyResponse(message={"content": prompt})


class DummyOpenAIModel:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

class DummyRetryStrategy:
    def __init__(self, max_attempts):
        self.max_attempts = max_attempts
