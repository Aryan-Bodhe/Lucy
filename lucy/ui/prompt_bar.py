from pathlib import Path
from rich.console import Console

from prompt_toolkit import PromptSession, HTML
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.key_binding import KeyBindings

from lucy.config import AGENT_PROMPT_HISTORY_FILE

class PromptBar:
    def __init__(self):
        self.username = Path.home().name
        kb = KeyBindings()

        @kb.add("enter")
        def _(event):
            event.current_buffer.validate_and_handle()

        @kb.add("escape", "enter")   # Alt+Enter
        def _(event):
            event.current_buffer.insert_text("\n")

        @kb.add("escape")
        def _(event):
            event.app_exit(result=None)

        self.session = PromptSession(
            history=FileHistory(AGENT_PROMPT_HISTORY_FILE),
            auto_suggest=AutoSuggestFromHistory(),
            key_bindings=kb
        )
    
    
    def input(self, is_password: bool=False):
        return self.session.prompt(
            HTML(f"<ansigreen><b>{self.username} ❯ </b></ansigreen>"),
            multiline=True,
            is_password=is_password
        )
    