import argparse
from lucy.logger import get_logger
from lucy.ui.renderer import ui
from lucy.app import run_app
from lucy.config import VERSION

logger = get_logger()

def main():
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

    subparsers.add_parser(
        "login",
        help="Store your OpenAI API key",
    )

    subparsers.add_parser(
        "logout",
        help="Remove your stored API key",
    )

    subparsers.add_parser(
        "doctor",
        help="Diagnose your Lucy installation (coming soon)",
    )

    args = parser.parse_args()

    try:
        match args.command:
            case "login":
                ui.render_login_flow()

            case "logout":
                ui.render_logout_flow()

            case "doctor":
                return
                ui.render_doctor()

            case _:
                run_app()
    except Exception:
        ui.render_error("An unexpected error occurred. Please retry.")
        logger.exception("Unexpected error occurred")

    except KeyboardInterrupt:
        logger.info("User exited application")
