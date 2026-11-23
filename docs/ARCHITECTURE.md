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

Resolve them only when relevant to the requested change, and update this list
when fixed.

- Python support differs between package metadata (>=3.10), README (3.12+), and
  session imports (`datetime.UTC` needs 3.11+).
- Session listing assumes entries are UUID directories with valid metadata; it
  scans a capped set before sorting, which need not contain the newest sessions.
- `UsageMetrics.cached_output_tokens` actually holds cache *write* (input)
  tokens. Renaming it changes the saved metadata schema.
- Ctrl+D at the prompt raises `EOFError`, which reaches `main`'s generic handler
  instead of the clean shutdown path used for Ctrl+C.

## Usage accounting

`compute_usage_metrics` returns usage for one turn, taken from
`metrics.latest_agent_invocation`. Strands' `metrics.accumulated_usage` spans
every call on the cached agent and must not be saved: `SessionManager` adds each
turn's usage into the per-model totals in `metadata.json`. OpenAI reports cached
tokens inside `inputTokens`, so cost bills them once at the cache rate.
`context_used_pct` is a percentage (0-100) of `MODEL_CONTEXT_WINDOW`.

## Inspection baseline

On 2026-11-23 the ignored `env/` used Python 3.14.4 with the editable package and
pytest installed. With `XDG_STATE_HOME` set to a temporary directory, the full
suite (`env/bin/python -m pytest -q`) passed: 111 tests.
