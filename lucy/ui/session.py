from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.prompt import Prompt

from lucy.session.manager import SessionManager

from lucy.config import MODEL
from lucy.ui.theme import SUCCESS, ERROR, PRIMARY, DEFAULT
from lucy.ui.constants import TICK, CROSS, SDOT, HDOT


class SessionUI:
    def __init__(self, console: Console):
        self.console = console
        self.session_mgr = SessionManager()

    def render_sessions_flow(self):
        self.console.print()
        self.console.print(
            Panel.fit(
                f"[{DEFAULT}]Scanning saved Lucy sessions...[{DEFAULT}]",
                title="Lucy Sessions",
                style=PRIMARY,
            )
        )
        self.console.print()

        sessions_list = self.session_mgr.list_sessions()
        sessions = sessions_list.sessions

        if not sessions:
            self.console.print(
                f"[{ERROR}]{CROSS}[/] No saved sessions found."
            )
            self.console.print()
            return

        self.console.print("[bold]Available Sessions[/bold]\n")

        for idx, session in enumerate(sessions, start=1):
            s_time = session.metadata.started_at.astimezone().strftime(f"%H:%M {HDOT} %d %b %Y")
            model_usage = session.metadata.usage.get(MODEL)

            if not model_usage:
                continue

            usage_cost = model_usage.cost_usd

            self.console.print(
                f"[bold]{idx:>2}.[/] "
                f"{escape(session.metadata.session_title or 'Untitled')} [dim]{str(session.session_id)[:8]}[/dim] "
                f"[dim]({s_time} {HDOT} ${usage_cost: .4f})[/dim]"
            )

        self.console.rule()
        self.console.print()
        if sessions_list.total_count <= sessions_list.requested_count:
            self.console.print(
                f"Found {sessions_list.total_count} saved session(s).\n"
            )
        else:
            self.console.print(
                f"Found {sessions_list.total_count} saved session(s). Showing only {sessions_list.requested_count} latest ones.\n"
            )
