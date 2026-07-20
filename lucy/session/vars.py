from contextlib import contextmanager
from contextvars import ContextVar
from uuid import uuid4


request_id_var: ContextVar[str] = ContextVar("request_id", default="-")
session_id_var: ContextVar[str] = ContextVar("session_id", default="-")

@contextmanager
def token_manager():
    request_id = str(uuid4())[:8]
    token = request_id_var.set(request_id)
    try:
        yield
    finally:
        request_id_var.reset(token)


@contextmanager
def session_manager():
    session_id = str(uuid4())[:8]
    token = session_id_var.set(session_id)
    try:
        yield
    finally:
        session_id_var.reset(token)