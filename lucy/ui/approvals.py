from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.text import Text

from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.logger import get_logger

logger = get_logger()

def _check_approval(s: str):
    return s.strip().lower() in {"", "y", "yes", "ok"}


class ApprovalUI:
    def __init__(self, console: Console):
        self.console = console

    def render_sudo_permission_request(self, tool_name: str, tool_command: str):
        try:
            approval_msg = SUDO_PERMISSION_REQUEST_TEXT.format(
                tool_name=tool_name, 
                tool_command=tool_command
            )
        except Exception:
            approval_msg = f"Enter sudo password to allow {tool_name} to run '{tool_command}' (y/*)"

        self.console.print(
            Panel.fit(
                approval_msg,
                style=WARNING
            )
        )
        return self.console.input("Password > ", password=True)


    def render_approval(self, tool_name: str, tool_command: str):
        try:
            approval_msg = TOOL_TEXT.format(
                tool_name=tool_name, 
                tool_command=tool_command
            )
        except Exception:
            approval_msg = f"Approve tool {tool_name} to run '{tool_command}'? [y/*]"

        approval = "no"
        with Live(
            Panel.fit(
                approval_msg,
                style=WARNING
            ),
            transient=True
        ) as live:
            approval = self.console.input(
                "> Press Enter to approve, type no to deny. "
            )
            live.update(Text(approval))

        return _check_approval(approval)