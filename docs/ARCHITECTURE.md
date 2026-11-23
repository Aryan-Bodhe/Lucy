# Lucy architecture

This is a source-based map for contributors. Recheck the linked modules when
changing behavior; limitations below describe the current checkout, not a roadmap.

## Execution flow

1. The installed `lucy` command calls `lucy.main:main`. It sets tool environment
   defaults, parses arguments with argparse, and calls `dispatch_command`.
2. The dispatcher sends `login`, `logout`, `doctor`, and `sessions` to UI flows.
   With no matching command it starts `run_app`. `usage` is advertised as coming
   soon but currently also falls through to the app.
3. `run_app` creates a `SessionManager`, enters `session_scope`, initializes the
   UI, shows the banner, and repeatedly calls `handle_request`.
4. `handle_request` reads the prompt, saves a user transcript event, enters a
   request scope, and calls `_handle_request`. That helper calls `run_agent`,
   extracts the response, and calculates current/accumulated usage.
5. `run_agent` lazily constructs and reuses a Strands `Agent` with an `OpenAIModel`.
   It obtains credentials from keyring, appends working-directory/date/timezone
   metadata to the prompt, invokes the model synchronously, and returns the
   Strands result with elapsed time.
6. Agent hooks render tool progress. The sensitive-tool intervention requests
   approval through `ui.approvals` before editor, shell, or Python tool calls.
7. The CLI saves the agent response and usage metadata, then renders the answer
   and a usage rule. Exiting session scope closes the store and resets context IDs.

## Components

| Location | Responsibility |
| --- | --- |
| `lucy/config.py` | App/model constants, cost settings, package-relative skill path, platformdirs state paths |
| `lucy/logger.py` | Rotating file logs with session/request IDs from context variables |
| `lucy/cli/` | Routing, interactive orchestration, usage calculations, credential helpers, diagnostic checks |
| `lucy/agent/` | Model/agent construction, tools, lifecycle hooks, interventions, tool parameter summaries |
| `lucy/agent/prompts/system_prompt.py` | Python string used as the agent system prompt |
| `lucy/agent/skills/` | Packaged skills loaded through Strands `AgentSkills`; currently `system-operations` |
| `lucy/ui/` | Rich renderers and prompt-toolkit input; composed by the module-level `ui` instance |
| `lucy/session/` | Pydantic schemas, file storage, session listing, scopes, context variables |
| `tests/` | pytest tests organized by subsystem, with local fixtures and dummy objects |

The source prompt and skill instructions describe Lucy's runtime behavior. They
are product assets, separate from instructions for agents editing this repository.

## Persistence and authentication

`platformdirs.user_state_dir(APP_NAME, APP_AUTHOR)` supplies the state directory.
Config creates it and its `sessions/` child at import time. History lives in
`history.txt`, and the logger writes `logs/app.log` with timed rotation.

Each `sessions/<uuid>/` contains:

- `metadata.json`: `SessionMetadata` with required `started_at`, optional
  `ended_at`, and `usage`, a dictionary keyed by model ID.
- `transcript.jsonl`: one serialized `TranscriptEvent` per line with timestamp,
  role (`user` or `agent`), and message. Initialization adds an agent event.

`SessionStore` handles file I/O. `SessionRepository` creates stores and lists
summaries. `SessionManager` owns the active store, scopes IDs with ContextVars,
and delegates reads/writes. Transcripts store user/agent text, not a serialized
Strands conversation or tool history. `SessionUI` lists summaries; it does not
currently implement resuming a model conversation.

The agent reads the keyring entry for `(APP_NAME, MODEL_PROVIDER)`. The login UI
checks the key prefix and writes the key directly; it does not call
`cli.auth.validate_api_key`. Diagnostics may validate a stored key by issuing a
model request. These paths should be tested with mocks.

## Known integration gaps to check when touching these areas

These observations come from source inspection, not a successful runtime suite.
Resolve them only when relevant to the requested change, and update this list
when fixed.

- Python support differs between package metadata (>=3.10), README (3.12+), and
  session imports (`datetime.UTC` needs 3.11+).
- `cli.app.handle_request` dereferences the result before its `None` guard, even
  though `_handle_request` can return `None` after rendering an error.
- Usage interfaces need reconciliation: `compute_accumulated_metrics` supplies
  `context_used`, while `UsageMetrics` defines `context_used_pct`, and the manager
  adds the provided usage to saved totals even when supplied accumulated values.
- `SAFE_TOOLS` has adjacent `"skills"` and `"current_time"` literals without a
  comma. The active approval intervention uses `SENSITIVE_TOOLS`, not this list.
- Session listing assumes entries are UUID directories with valid metadata; it
  scans a capped set before sorting, which need not contain the newest sessions.
- Several tests use older APIs: metadata as a single usage object, an
  `ExecutionMetrics` type no longer defined, a `lucy` transcript role, and
  `handle_request(prompt)` rather than `handle_request(session_manager)`.

## Inspection baseline

During agent documentation setup on 2026-11-23, the existing ignored `env/`
contained Python symlinks targeting a missing `/usr/bin/python3.12`. System
Python was 3.14.4 with pytest 9.0.2. Running
`XDG_STATE_HOME=/tmp/lucy-agent-onboarding-state python3 -m pytest --collect-only -q`
stopped with eight collection errors for missing `keyring`, `pydantic`,
`colorama`, and `openai`. No test pass/fail baseline was established. Recreate a
working environment and collect again before attributing failures to a change.
