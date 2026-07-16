from rich.console import Console

from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.logger import get_logger

from lucy.config import AGENT_NAME

logger = get_logger()


class ResponseUI:
    def __init__(self, console: Console):
        self.console = console

    def render_response(self, response: str):
        self.console.print(
            f"[bold {PRIMARY}]{AGENT_NAME} ❯ [/bold {PRIMARY}]",
            end=""
        )
        self.console.print(response)

    def render_error(self, error_msg: str):
        self.console.print(
            f"[bold {ERROR}]{AGENT_NAME} ❯  {error_msg}[/bold {ERROR}]",
        )
