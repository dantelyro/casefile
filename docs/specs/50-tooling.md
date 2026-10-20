# Lint and test tooling

ruff and pytest, run through uv as development dependencies, adopted in their own milestone after M3.
Only development uses them: the hooks and scripts users run stay standard library (see D-048).

### TOOL-001 · The code passes ruff      [MVP]
Given the repository's Python code
When `uv run ruff check` runs with ruff's default rules
Then it exits 0: every finding is fixed in the code, and a `noqa` is allowed only with its reason, where
the code is right as written.

### TOOL-002 · Lint and tests run before every commit      [MVP]
Given `.claude/devflow.json`
When a commit touches the repository
Then the `devflow` app's `install` is `uv sync`, its `test` is `uv run pytest` and its `lint` is
`uv run ruff check`, so pre_commit refuses the commit on a failing test or a finding.

### TOOL-003 · The suite is written for pytest      [MVP]
Given the test suite
When it is run with `uv run pytest`
Then every test of today still exists and passes, written with plain `assert`, fixtures and
`parametrize` instead of `unittest.TestCase`, and each test's name still starts with its rule ID.

### TOOL-004 · Shipped code stays standard library      [MVP]
Given the code under `hooks/` and `skills/`
When its imports are checked
Then it imports nothing outside the standard library; only `tests/` may import pytest (D-048).

### TOOL-005 · ruff and pytest are uv dev dependencies      [MVP]
Given the repository
When the tools are installed
Then `pyproject.toml` lists ruff and pytest as development dependencies, `uv.lock` is committed, and
`.venv/` is ignored.
