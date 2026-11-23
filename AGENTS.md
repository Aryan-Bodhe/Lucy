# Working on Lucy

Lucy is a terminal AI coding assistant, distributed as the `lucy-code` Python
package with a `lucy` console command. It uses Strands Agents, an OpenAI model,
Rich, prompt-toolkit, OS keyring credentials, and local JSON/JSONL session files.

## Start here

- Read `README.md` for user-facing usage and `docs/ARCHITECTURE.md` for execution
  flow, module ownership, and current limitations.
- Read `tests/AGENTS.md` before changing tests or relying on test results.
- Treat source and `pyproject.toml` as the current implementation. Some README
  claims and test fixtures describe older or planned behavior.
- Inspect `git status --short` before editing; preserve unrelated work.
- Keep changes scoped to the task. Follow the surrounding Python style rather
  than reformatting whole modules. Keep these docs current when changing their
  described interfaces or commands.

## Setup and commands

Use Python 3.12+ for development. `pyproject.toml` declares >=3.10, but session
code imports `datetime.UTC` (available from 3.11); the README recommends 3.12+.
Do not assume the ignored `env/` works on a new machine.

```bash
python3 --version
python3 -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest --collect-only -q
.venv/bin/python -m pytest -q tests/agent
.venv/bin/python -m pytest -q
.venv/bin/lucy --help
.venv/bin/lucy --version
```

These paths are for POSIX shells; Windows uses `.venv\Scripts\python.exe` and
`.venv\Scripts\lucy.exe`. Use the environment's interpreter consistently.

- Runtime dependencies are declared in `pyproject.toml`; `requirements.txt` is
  a frozen environment snapshot, not a separate development dependency list.
- `makefile` uses `env/bin/`, not `.venv/bin/`. `make dev` installs packaging tools
  and the editable package, but does not install pytest, Black, or Ruff.
- `make test`, `make fmt`, and `make lint` require their tools to be installed in
  `env/`. There is no checked-in formatter/linter configuration. Avoid broad
  formatting as an incidental change.
- CI (`.github/workflows/tests.yml`) installs `.[dev]` and runs the full pytest
  suite on Python 3.12-3.14 for pushes to `main` and every pull request. Add new
  test-only dependencies to the `dev` extra so CI and local setups match.
- Build checks, when packaging is affected: install `build` and `twine` in the
  chosen environment, then run `python -m build` and `python -m twine check dist/*`
  with that environment's interpreter. Review package-data rules when changing
  skills or prompts. Publishing is a separate, explicitly requested operation.
- `lucy/main.py` defines the entry function but has no `__main__` invocation;
  use the installed console script instead of `python -m lucy`.

## Where to make changes

| Concern | Primary files | Related tests |
| --- | --- | --- |
| CLI arguments and routing | `lucy/main.py`, `lucy/cli/dispatcher.py` | `tests/test_main.py`, `tests/cli/test_dispatcher.py` |
| Interactive request loop and usage | `lucy/cli/app.py`, `lucy/cli/utils.py` | `tests/cli/test_app.py`, `tests/cli/test_utils.py` |
| Agent/model lifecycle | `lucy/agent/agent.py` | `tests/agent/test_agent.py` |
| Tool registration, progress, consent | `lucy/agent/tools.py`, `hooks.py`, `interventions.py`, `utils.py` | `tests/agent/`, `tests/ui/test_approvals.py` |
| Prompt and packaged skills | `lucy/agent/prompts/system_prompt.py`, `lucy/agent/skills/` | Agent tests; inspect built package when changing assets |
| Credentials and diagnostics | `lucy/cli/auth.py`, `doctor.py`, `lucy/ui/auth.py`, `doctor.py` | `tests/cli/`, `tests/ui/` |
| Session persistence and IDs | `lucy/session/` | `tests/session/` |
| Terminal presentation/input | `lucy/ui/` | `tests/ui/` |
| Settings and logging | `lucy/config.py`, `lucy/logger.py` | Check callers and affected subsystem tests |

Paths abbreviated within a cell are relative to the first named directory.

## Boundaries to preserve

- Keep argument parsing/routing, agent execution, terminal rendering, and session
  storage in their existing layers. The shared UI instance is `lucy.ui.core.ui`.
- The agent is lazily created and cached in `lucy.agent.agent._agent`; tests must
  reset it when varying construction settings. `AgentSkills` is created at import.
- Register executable tools in `ALL_TOOLS`. Changes to tools also require checking
  `SENSITIVE_TOOLS`, `parse_tool_parameters`, hooks, approvals, and their tests.
- `main.py` sets `BYPASS_TOOL_CONSENT=true` and `EDITOR_DISABLE_BACKUP=true` before
  importing tools. Lucy's own `SensitiveToolApproval` intervention provides the
  consent UI for editor, shell, and Python execution. Preserve that boundary;
  prompt wording alone is not enforcement.
- `SudoPasswordHandler` exists but is not registered in the active agent. Do not
  assume automatic privilege escalation is implemented.
- Session files are user data: metadata JSON plus an append-only transcript JSONL
  under UUID directories. When changing models, consider existing saved files and
  add meaningful compatibility/round-trip checks for the requested behavior.
- Active logging context IDs come from `lucy/session/vars.py`; `cli/context.py`
  defines separate variables and is not the active session manager.
- Version is duplicated in `pyproject.toml` and `lucy/config.py`; synchronize both
  when a version change is requested. Model and cost settings live in config.

## Credentials, runtime state, and verification

- Do not read or expose `.env`, secrets, keyring contents, personal transcripts,
  history, or logs unless the task requires it and the user authorizes access.
  Do not commit these files or local environments/build artifacts.
- API keys use keyring with `APP_NAME` and the provider ID. Do not add hard-coded
  keys or silently replace keyring storage with a plaintext file.
- Importing config creates state/session directories; logger initialization opens
  a log file; importing the shared UI constructs a prompt session. On Linux, run
  checks with `XDG_STATE_HOME` set to a temporary directory to isolate user state:

  ```bash
  XDG_STATE_HOME="$(mktemp -d)" .venv/bin/python -m pytest --collect-only -q
  ```

- Unit tests should mock model calls, credentials, subprocesses, and interactive
  input. Do not use live `lucy`, `login`, `logout`, or `doctor` as routine tests:
  they can prompt, change credentials, contact the network, or incur model usage.
- Start with affected tests and collection, then run the full suite. Consult the
  test guide before changing tests; use a bounded test process when touching the
  interactive loop.
- Report commands run and distinguish environment/collection failures, existing
  source-test drift, and regressions. Do not claim tests passed when collection
  failed, or weaken tests solely to hide failures.
