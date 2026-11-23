# Testing Lucy

Follow the root `AGENTS.md` and use the same Python environment as the editable
package. Tests use pytest and monkeypatch; no coverage or async test runner is
configured. Read the nearest `conftest.py` and `_helpers.py` before extending a
suite.

## Isolation patterns

- Agent tests reset `lucy.agent.agent._agent` and replace the model and agent
  constructors with dummies. `_skills` is constructed at module import, so
  patching `AgentSkills` afterward does not recreate it.
- Patch dependencies where the code under test imports/looks them up. For
  example, session fixtures patch `SESSIONS_DIR` in both store and repository;
  changing only `lucy.config.SESSIONS_DIR` after import is insufficient.
- Use `tmp_path` for session files and explicit timestamps for deterministic
  ordering. Cover schema validation and persistence round trips when those
  contracts change.
- Mock keyring operations, model/network calls, subprocess/sudo calls, terminal
  input, and Rich rendering as needed. UI tests use dummy consoles; tests must
  not ask for passwords or interact with a real credential store.
- Config/logging can create files before fixtures run. On Linux, set a temporary
  `XDG_STATE_HOME` before starting pytest, as shown in the root guide.

## Existing drift

Collection succeeding does not mean the suite matches current production APIs.
Session fixtures still reference missing `ExecutionMetrics`, old metadata shapes,
and old manager signatures; model tests also expect the old `lucy` role. CLI
fixtures and tests include an older request/context lifecycle. Compare fixtures
against source before deciding whether the implementation or expectation is wrong.

In particular, `tests/cli/test_app.py::test_run_app_happy_path` replaces
`handle_request` with a function that returns immediately, but the current
`run_app` loop ignores that return value. The mocked render function that raises
`StopIteration` may never be called, leaving the test looping indefinitely. Use
a bounded test process until that test is updated for the current lifecycle.

For a feature or fix, add focused tests for the intended behavior, run the
affected subset, and report pre-existing failures separately. Do not bulk-rewrite
stale suites or remove assertions as incidental cleanup. The documented setup
baseline is in `docs/ARCHITECTURE.md`; it records collection failures, not passes.
