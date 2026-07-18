import os

# Set necessary environment vars before any imports
os.environ.setdefault("BYPASS_TOOL_CONSENT", "true")
os.environ.setdefault("EDITOR_DISABLE_BACKUP", "true")

import argparse
from lucy.logger import get_logger
from lucy.ui.core import ui
from lucy.cli.dispatcher import dispatch_command, SUBCOMMANDS
from lucy.config import VERSION

logger = get_logger()

def parse_args():
    parser = argparse.ArgumentParser(
        prog="lucy",
        description="Lucy — Your AI coding copilot.",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"Lucy v{VERSION}",
    )

    subparsers = parser.add_subparsers(dest="command")

    for command, helptext in SUBCOMMANDS.items():
        subparsers.add_parser(name=command, help=helptext)

    args = parser.parse_args()
    return args

def main():
    try:
        args = parse_args()
        dispatch_command(args)

    except KeyboardInterrupt:
        logger.info("User exited application")

    except Exception:
        ui.responses.render_error("An unexpected error occurred. Please retry.")
        logger.exception("Unexpected error occurred")
main()