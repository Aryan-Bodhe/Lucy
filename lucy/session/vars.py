from contextlib import contextmanager
from contextvars import ContextVar
from uuid import uuid4


request_id_var: ContextVar[str] = ContextVar("request_id", default=None)
session_id_var: ContextVar[str] = ContextVar("session_id", default=None)

