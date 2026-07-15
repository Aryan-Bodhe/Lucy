from pathlib import Path
from platformdirs import user_state_dir

# App configuration
APP_NAME = "Lucy"
APP_AUTHOR = "Aryan Bodhe"
VERSION = "1.0.0"

PACKAGE_DIR = Path(__file__).resolve().parent
SKILLS_DIR = PACKAGE_DIR / "agent" / "skills"

# Local storage configuration
STATE_DIR = Path(user_state_dir(APP_NAME, APP_AUTHOR))
LOGGING_DIR = Path(user_state_dir(APP_NAME, APP_AUTHOR)) / "logs"
STATE_DIR.mkdir(parents=True, exist_ok=True)

# Agent configuration
AGENT_NAME = "Lucy"
AGENT_PROMPT_HISTORY_FILE = str(STATE_DIR / "history.txt")
CLEAR_TERMINAL_UPON_EXIT = False

# Model parameters
MODEL = "gpt-5.4-mini"
MODEL_PROVIDER = "openai"
MODEL_CONTEXT_WINDOW = 400_000
MODEL_INPUT_COST_PM = 0.75
MODEL_CACHE_COST_PM = 0.075
MODEL_OUTPUT_COST_PM = 4.50

# Logging configuration
LOGGING_LIMIT_DAYS = 7
LOG_TO_CONSOLE = False
