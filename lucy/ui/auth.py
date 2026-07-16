from getpass import getpass

import keyring
from rich.panel import Panel
from rich.console import Console
from rich.prompt import Confirm

from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.logger import get_logger

from lucy.config import (
    AGENT_NAME,
    APP_NAME,
    MODEL,
    MODEL_PROVIDER
)

logger = get_logger()

class AuthUI:
    def __init__(self, console: Console):
        self.console = console

    def render_login_flow(self):
        self.console.print()

        self.console.print(
            Panel.fit(
                f"[bold {PRIMARY}]Welcome to {AGENT_NAME}! 👋[/bold {PRIMARY}]\n\n"
                f"{AGENT_NAME} currently uses [bold {ACCENT}]OpenAI[/bold {ACCENT}] with "
                f"[bold {ACCENT}]{MODEL}[/bold {ACCENT}].\n\n"
                "You'll need an OpenAI API key to continue.",
                title="Lucy Setup",
                border_style=f"{PRIMARY}",
            )
        )

        self.console.print(
            "[dim]You can create one at:[/dim] "
            "https://platform.openai.com/api-keys\n"
        )

        if not Confirm.ask("Do you already have an API key?", default=True):
            self.console.print(
                f"\nCreate one first, then run [bold {ACCENT}]lucy login[/bold {ACCENT}] again.\n"
            )
            return

        while True:
            api_key = getpass(f"{HDOT} OpenAI API Key (paste and hit Enter): ").strip()

            if not api_key.startswith("sk-"):
                self.console.print(
                    f"[bold {ERROR}]{SDOT} That doesn't look like a valid OpenAI API key.[/bold {ERROR}]\n"
                )
                continue

            break

        keyring.set_password(APP_NAME, MODEL_PROVIDER, api_key)

        self.console.print(
            f"\n[bold {SUCCESS}]{SDOT} Setup complete![/bold {SUCCESS}]\n\n"
            "You can now start Lucy by running \n"
            f"  [bold {ACCENT}]lucy[/bold {ACCENT}]\n"
            "in the terminal.\n"
        )

    def render_logout_flow(self):
        self.console.print()

        try:
            api_key = keyring.get_password(APP_NAME, MODEL_PROVIDER)

            if api_key is None:
                self.console.print(
                    Panel.fit(
                        f"[yellow]{SDOT} You're already logged out.[/yellow]",
                        title="Logout",
                        border_style="yellow",
                    )
                )
                return

            keyring.delete_password(APP_NAME, MODEL_PROVIDER)

            self.console.print(
                Panel.fit(
                    f"[bold green]{SDOT} Successfully logged out.[/bold green]\n\n"
                    "Your stored API key has been removed.",
                    title="Lucy Logout",
                    border_style="green",
                )
            )

        except keyring.errors.KeyringError as e:
            self.console.print(
                Panel.fit(
                    f"[red]{SDOT} Failed to remove credentials.[/red]\n\n{e}",
                    title="Error",
                    border_style="red",
                )
            )
