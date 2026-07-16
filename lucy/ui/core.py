import os
import time
from contextlib import contextmanager
from getpass import getpass

from rich.console import Console

from lucy.ui.prompt_bar import PromptBar
from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.ui.approvals import ApprovalUI
from lucy.ui.auth import AuthUI
from lucy.ui.banner import BannerUI
from lucy.ui.responses import ResponseUI
from lucy.ui.tools import ToolUI

from lucy.logger import get_logger

from lucy.config import (
    MODEL_CACHE_COST_PM,
    MODEL_CONTEXT_WINDOW,
    MODEL_INPUT_COST_PM,
    MODEL_OUTPUT_COST_PM
)

logger = get_logger()


class RequestSession:
    def __init__(self, console: Console, prompt_bar: PromptBar):
        self._console = console
        self._prompt_bar = prompt_bar
        self.usage: dict = None
        self.time_elapsed: float = None
        self.response = []

    def input(self) -> str:
        return self._prompt_bar.input()
    
    def print(self, *args, **kwargs):
        self._console.print(*args, **kwargs)


def _get_request_stats_title(self, session: RequestSession):
        if session.usage:
            input = session.usage.get("inputTokens", 0)
            output = session.usage.get("outputTokens", 0)
            cache = session.usage.get("cacheReadInputTokens", 0)
            time = session.time_elapsed
            input_cost = MODEL_INPUT_COST_PM * input / 1_000_000
            output_cost = MODEL_OUTPUT_COST_PM * output / 1_000_000
            cache_cost = MODEL_CACHE_COST_PM * output / 1_000_000
            context_used_pct = round((input + output + cache) / MODEL_CONTEXT_WINDOW, 2)
            req_cost = round(input_cost + output_cost + cache_cost, 4)
            return f"Input={input} Output={output} Time={time}s Context_used={context_used_pct}% Cost=${req_cost}"
        return ""


class _UI:
    def __init__(self):
        self.console = Console()
        self.prompt_bar = PromptBar()

        self.session = RequestSession(self.console, self.prompt_bar)
        
        self.approvals = ApprovalUI(self.console)
        self.auth = AuthUI(self.console)
        self.banner = BannerUI(self.console)
        self.responses = ResponseUI(self.console)
        self.tools = ToolUI(self.console)
        
    
    def initialise(self):
        os.system("clear")
        self.console.clear()


    def terminate(self, clear_terminal: bool = False):
        self.responses.render_response(SIGNOFF_TEXT)
        self.console.print()
        if clear_terminal:
            time.sleep(2)
            self.console.clear()


    @contextmanager
    def render_request_lifecycle(self):
        session = self.session
        try:
            yield session
        finally:
            try:
                title = _get_request_stats_title(session)
            except Exception as exc:
                logger.exception("Failed to print metrics")
                title = ""
            self.console.print()
            self.console.rule(
                style=SUCCESS,
                title=title
            )
        

ui = _UI()