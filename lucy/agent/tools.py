from strands_tools import (
    editor,
    shell,
    current_time,
    python_repl,
    handoff_to_user
)
from lucy.logger import get_logger

logger = get_logger()


SENSITIVE_TOOLS = [
    "editor",
    "python_repl",
    "shell"
]

SAFE_TOOLS = [
    "skills"
    "current_time",
    "handoff_to_user"
]

ALL_TOOLS = [
    editor,
    shell,
    current_time,
    python_repl,
    handoff_to_user,
]