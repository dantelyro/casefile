# Lint and test tooling

ruff and pytest, run through uv as development dependencies, adopted in their own milestone, the next after M1.
Tests test code, not tools (ruled 2026-10-20): the tooling rules are enforced by the tools, the commit
gate and CI, and checked in review; only TOOL-004, a property of the shipped code, has a test.
Only development uses them: the hooks and scripts users run stay standard library (see D-048).

### TOOL-001 · The code passes ruff      [MANUAL]
Given the repository's Python code
When `uv run ruff check` runs with ruff's default rules, in the commit gate (TOOL-002) and as its own CI
step
Then it exits 0: every finding is fixed in the code, and a `noqa` is allowed only with its reason, where
the code is right as written. No test runs ruff: the linter's exit is the check, and the reviewer checks
each `noqa` for its reason.

### TOOL-002 · Lint and tests run before every commit      [MANUAL]
Given `.claude/devflow.json`
When a commit touches the repository
Then the `devflow` app's `install` is `uv sync`, its `test` is `uv run pytest` and its `lint` is
`uv run ruff check`, so pre_commit refuses the commit on a failing test or a finding. No test reads the configuration: a
wrong command fails the gate itself.

### TOOL-003 · The suite is written for pytest      [MANUAL]
Given the test suite
When it is run with `uv run pytest`
Then every test of today still exists and passes, written with plain `assert`, fixtures and
`parametrize` instead of `unittest.TestCase`, and each test's name still starts with its rule ID.
The reviewer checks the style and that no test was lost; no test checks other tests.

### TOOL-004 · Shipped code stays standard library      [MVP]
Given the code under `hooks/` and `skills/`
When its imports are checked
Then it imports nothing outside the standard library; only `tests/` may import pytest (D-048).

### TOOL-005 · ruff and pytest are uv dev dependencies      [MANUAL]
Given the repository
When the tools are installed
Then `pyproject.toml` lists ruff and pytest as development dependencies, `uv.lock` is committed, and
`.venv/` is ignored. CI runs `uv sync --locked`, which fails on a stale lock; no test checks the
tooling.
