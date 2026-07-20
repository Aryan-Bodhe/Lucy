from session.repository import SessionRepository
from session.store import SessionStore

from logger import get_logger

logger = get_logger()

class SessionManager:
    def __init__(self):
        self.repo = SessionRepository()
        