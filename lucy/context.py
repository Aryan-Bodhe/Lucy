from contextlib import contextmanager
from contextvars import ContextVar
from uuid import uuid4


request_id_var: ContextVar[str] = ContextVar("request_id", default="-")

@contextmanager
def token_manager():
    request_id = str(uuid4())[:8]
    token = request_id_var.set(request_id)
    try:
        yield
    finally:
        request_id_var.reset(token)