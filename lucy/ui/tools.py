from typing import Literal

from rich.console import Console

from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.logger import get_logger

logger = get_logger()


class ToolUI:
    def __init__(self, console: Console):
        self.console = console

    def render_status(
        self, 
        tool_name: str, 
        tool_command: str, 
        status: Literal["running", "failed", "success", "refused"],
        tool_type: Literal["tool", "skill"] = "tool"
    ):
        self.console.print()

        text = "Running tool" if tool_type == "tool" else "Reading skill"
        if status == "running":
            self.console.print(f"{HDOT}[bold] {text}([/bold]{tool_name}[bold])[/bold]")
        elif status == "failed":
            self.console.print(f"[{ERROR}]{SDOT}[/{ERROR}][bold] Error {text.lower()}([/bold]{tool_name}[bold])[/bold]")
        elif status == "success":
            text = "running tool" if tool_type == "tool" else "reading skill"
            self.console.print(f"[{SUCCESS}]{SDOT}[/{SUCCESS}][bold] Finished {text.lower()}([/bold]{tool_name}[bold])[/bold]")
        elif status == "refused":
            self.console.print(f"[{ERROR}]{SDOT}[/{ERROR}][bold] User denied tool([/bold]{tool_name}[bold])[/bold]")

        if tool_type == "tool":
            self.console.print(f"   ∟ {tool_command}")