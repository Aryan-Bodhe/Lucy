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

## Keeping the suite trustworthy

The full suite was brought in line with current production APIs on 2026-11-23
and passes without deselection. When a test fails, decide whether the test or
the code reflects the intended behavior before changing either; a test that
asserts current buggy behavior is worse than no test.

For a feature or fix, add focused tests for the intended behavior and confirm a
regression test fails without the fix. Run the affected subset, then the full
suite. Do not remove assertions to make a run pass.
