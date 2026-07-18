import os
import sys
import socket
import tempfile
from dataclasses import dataclass
from pathlib import Path
from shutil import which
from typing import Callable, Literal
from openai import APIConnectionError

from lucy.cli.auth import get_api_key, validate_api_key
from lucy.config import LOGGING_DIR, VERSION, SUPPORTED_PROVIDERS


Status = Literal["passed", "failed", "warning", "skipped"]


@dataclass(slots=True)
class CheckResult:
    name: str
    status: Status
    details: str
    fix: str | None = None


Check = Callable[[], CheckResult]


REQUIRED_ENV_VARS = [
    "BYPASS_TOOL_CONSENT",
    "EDITOR_DISABLE_BACKUP",
]


def check_git() -> CheckResult:
    git = which("git")

    if git:
        return CheckResult(
            "Git",
            "passed",
            git,
        )

    return CheckResult(
        "Git",
        "failed",
        "Not installed",
        "Install Git and ensure it is available in PATH.",
    )


def check_internet() -> CheckResult:
    try:
        socket.create_connection(("api.openai.com", 443), timeout=3).close()

        return CheckResult(
            "Internet",
            "passed",
            "Connected",
        )

    except OSError:
        return CheckResult(
            "Internet",
            "warning",
            "Offline",
            "Lucy requires an internet connection.",
        )


def check_directory(name: str, path: Path) -> CheckResult:
    try:
        path.mkdir(parents=True, exist_ok=True)

        with tempfile.NamedTemporaryFile(dir=path):
            pass

        return CheckResult(
            name,
            "passed",
            str(path),
        )

    except Exception:
        return CheckResult(
            name,
            "failed",
            str(path),
            "Directory is not writable.",
        )


def check_logs_dir() -> CheckResult:
    return check_directory("Logs", LOGGING_DIR)


def check_path() -> CheckResult:
    path = which("lucy")

    if path:
        return CheckResult(
            "PATH",
            "passed",
            path,
        )

    return CheckResult(
        "PATH",
        "warning",
        "Lucy not found in PATH",
        "Restart your terminal or add Lucy to PATH.",
    )


def check_environment_vars() -> CheckResult:
    missing = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]

    if not missing:
        return CheckResult(
            "Environment",
            "passed",
            "Configured",
        )

    return CheckResult(
        "Env Vars",
        "warning",
        f"Missing: {', '.join(missing)}",
        "Some integrations may not behave as expected.",
    )


def check_version() -> CheckResult:
    return CheckResult(
        "Lucy",
        "passed",
        VERSION,
    )


def check_api_keys() -> CheckResult:
    configured_providers = []
    invalid_providers = []
    skipped_providers = []

    for provider, validation_model in SUPPORTED_PROVIDERS:
        key = get_api_key(provider)

        if not key:
            continue

        try:
            if validate_api_key(key, provider, validation_model):
                configured_providers.append(provider)
            else:
                invalid_providers.append(provider)

        except APIConnectionError:
            skipped_providers.append(provider)

    details = []

    if configured_providers:
        details.append(
            f"Configured: {', '.join(configured_providers)}"
        )

    if invalid_providers:
        details.append(
            f"Invalid: {', '.join(invalid_providers)}"
        )

    if skipped_providers:
        details.append(
            f"Validation skipped: {', '.join(skipped_providers)}"
        )

    details = " | ".join(details)

    # Everything validated successfully
    if configured_providers and not invalid_providers and not skipped_providers:
        return CheckResult(
            "API Keys",
            "passed",
            details,
        )

    # Some valid, some invalid and/or skipped
    if configured_providers:
        return CheckResult(
            "API Keys",
            "warning",
            details,
            "Some API keys could not be validated or are invalid.",
        )

    # No valid keys, but validation couldn't happen
    if skipped_providers:
        return CheckResult(
            "API Keys",
            "warning",
            details,
            "Unable to validate API keys because there is no internet connection.",
        )

    # All configured keys are invalid
    if invalid_providers:
        return CheckResult(
            "API Keys",
            "failed",
            details,
            "Run 'lucy login' to update your API keys.",
        )

    # Nothing configured
    return CheckResult(
        "API Keys",
        "failed",
        "No providers configured.",
        "Run 'lucy login'.",
    )


def check_python() -> CheckResult:
    version = sys.version_info
    current = f"{version.major}.{version.minor}.{version.micro}"

    if version < (3, 10):
        return CheckResult(
            "Python",
            "failed",
            current,
            "Lucy requires Python 3.10 or newer.",
        )

    if version < (3, 12):
        return CheckResult(
            "Python",
            "warning",
            current,
            "Python 3.12+ is recommended for the best experience.",
        )

    return CheckResult(
        "Python",
        "passed",
        current,
    )


CHECKS: list[Check] = [
    # Core installation
    check_version,
    check_python,
    check_git,
    check_path,
    check_logs_dir,

    # Connectivity
    check_internet,

    # Authentication
    check_api_keys,

    # Optional environment
    check_environment_vars,
]


def run_doctor():
    """Yield doctor check results as they complete."""
    for check in CHECKS:
        yield check()