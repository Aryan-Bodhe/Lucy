import os

from pyfiglet import Figlet
from rich.panel import Panel
from rich.console import Console

from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.logger import get_logger

from lucy.config import (
    AGENT_NAME,
    VERSION,
    MODEL
)

logger = get_logger()

class BannerUI:
    def __init__(self, console: Console):
        self.console = console

    def render(self):
        figlet = Figlet(font="ansi_shadow")
        text = figlet.renderText(AGENT_NAME+" .AI")
        self.console.print(
            Panel(
                f"[bold {PRIMARY}]{text}[/bold {PRIMARY}]",
                border_style=PRIMARY
            )
        )
        self.console.print(
            f"[bold]{WELCOME_TEXT}[/bold]\n", 
            style=PRIMARY
        )
        self.console.print(
            f"[bold {ACCENT}]{AGENT_NAME} v{VERSION} [/bold {ACCENT}]•[bold {ACCENT}] {MODEL} [/bold {ACCENT}]•[bold {ACCENT}] {os.getcwd()}[/bold {ACCENT}]", 
            highlight=False
        )
        self.console.rule()