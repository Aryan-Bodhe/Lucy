import os
import time
from typing import Literal
from contextlib import contextmanager
from getpass import getpass

import keyring
from pyfiglet import Figlet
from rich.panel import Panel
from rich.console import Console
from rich.live import Live
from rich.prompt import Confirm
from rich.text import Text

from lucy.ui.prompt_bar import PromptBar
from lucy.ui.theme import *
from lucy.ui.constants import *

from lucy.logger import get_logger

from lucy.config import (
    AGENT_NAME,
    APP_NAME,
    VERSION,
    MODEL,
    MODEL_PROVIDER,
    MODEL_CACHE_COST_PM,
    MODEL_CONTEXT_WINDOW,
    MODEL_INPUT_COST_PM,
    MODEL_OUTPUT_COST_PM
)

logger = get_logger()


def _check_approval(s: str):
    return s.strip().lower() in {"", "y", "yes", "ok"}


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



class _UI:
    def __init__(self):
        self.console = Console()
        self.prompt_bar = PromptBar()
        self.session = RequestSession(self.console, self.prompt_bar)
    
    def initialise(self):
        os.system("clear")
        self.console.clear()

    def terminate(self, clear_terminal: bool = False):
        self.render_response(SIGNOFF_TEXT)
        self.console.print()
        if clear_terminal:
            time.sleep(2)
            self.console.clear()

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

    def render_banner(self):
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
    

    def render_tool_status(
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
    

    def render_plan(self, plan: str):
        self.console.print(
            Panel(
                plan,
                title="Plan",
                style=ACCENT,
                border_style=ACCENT
            )
        )
        self.console.print(
            PLAN_APPROVAL_TEXT,
            style=WARNING
        )   
        approval = self.console.input()
        return _check_approval(approval)
    
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


    @contextmanager
    def render_request_lifecycle(self):
        session = self.session
        try:
            yield session
        finally:
            try:
                title = self._get_request_stats_title(session)
            except Exception as exc:
                logger.exception("Failed to print metrics")
                title = ""
            self.console.print()
            self.console.rule(
                style=SUCCESS,
                title=title
            )
        

ui = _UI()