from argparse import Namespace

from lucy.ui.core import ui
from lucy.cli.app import run_app

SUBCOMMANDS = {
    "login" :   "Login with an API key",
    "logout":   "Remove your stored API key",
    "doctor":   "Diagnose your installation",
    "usage" :   "Get usage statistics (coming soon)"
}

def dispatch_command(args: Namespace):
    match args.command:
        case "login":
            ui.auth.render_login_flow()

        case "logout":
            ui.auth.render_logout_flow()

        case "doctor":
            ui.doctor.render_doctor_flow()

        case _:
            run_app()