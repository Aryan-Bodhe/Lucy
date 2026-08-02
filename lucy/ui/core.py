import os
import time
from contextlib import contextmanager

from rich.console import Console

from lucy.ui.prompt_bar import PromptBar
from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.ui.approvals import ApprovalUI
from lucy.ui.auth import AuthUI
from lucy.ui.banner import BannerUI
from lucy.ui.responses import ResponseUI
from lucy.ui.tools import ToolUI
from lucy.ui.doctor import DoctorUI
from lucy.ui.session import SessionUI

from lucy.session.models import UsageMetrics
from lucy.logger import get_logger

from lucy.config import (
    MODEL_CACHE_COST_PM,
    MODEL_CONTEXT_WINDOW,
    MODEL_INPUT_COST_PM,
    MODEL_OUTPUT_COST_PM
)

logger = get_logger(__name__)


class _UI:
    def __init__(self):
        self.console = Console()
        self.prompt_bar = PromptBar()
        
        self.approvals = ApprovalUI(self.console)
        self.auth = AuthUI(self.console)
        self.banner = BannerUI(self.console)
        self.responses = ResponseUI(self.console)
        self.tools = ToolUI(self.console)

        self.doctor = DoctorUI(self.console)
        self.session = SessionUI(self.console)
        
    
    def initialise(self):
        os.system("clear")
        self.console.clear()

    def input(self):
        return self.prompt_bar.input()

    def print(self, msg: str = ""):
        self.console.print(msg)


    def terminate(self, clear_terminal: bool = False):
        self.responses.render_response(SIGNOFF_TEXT)
        self.console.print()
        if clear_terminal:
            time.sleep(2)
            self.console.clear()

    def rule(self, title: str):
        self.console.rule(
            style=SUCCESS,
            title=title
        )
        

ui = _UI()
