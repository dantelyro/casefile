# D-048 — Development uses uv, pytest and ruff; only shipped code stays standard library

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-19: answers 'Rewrite to pytest', 'Fix all in code' and 'pyproject + uv venv' to the M4 questions, after asking what a rewrite gains; then 'yes' to the redraft.

**Context:** D-027 made devflow standard-library Python, tested with unittest, with nothing ever downloaded, and a test fails on any import outside the standard library in hooks/, skills/ and tests/. On 2026-10-19 ruff 0.17.1 with its default rules reported 51 findings in hooks/ and tests/, and the developer chose to adopt ruff together with pytest as milestone M4.

**Options:** (a) pytest only as a runner of the unchanged unittest suite, D-027 kept whole; (b) the suite rewritten in pytest's style (plain assert, fixtures, parametrize), D-027 narrowed to shipped code; for installing the tools, (1) pinned uvx tools with no project files, or (2) dev dependencies in pyproject.toml with uv.lock committed and a uv venv.

**Decision:** (b) with (2). Tests import pytest; ruff and pytest are uv dev dependencies (pyproject.toml, uv.lock committed, .venv/ ignored); the devflow app runs uv sync, uv run pytest and uv run ruff check. Every ruff finding is fixed with ruff's default rules. The hooks and scripts users run stay standard library and download nothing: D-027 still holds for hooks/ and skills/, and the import test is narrowed to them.

**Trade-offs:** The suite no longer runs with a bare Python: every contributor and every pre-commit run needs uv. All 214 existing tests are rewritten, with behaviour unchanged, which is work with nothing new for users. The pre-commit gate gains a lint run on every commit. Users of the plugin are unaffected: pyproject.toml and uv.lock ship in the plugin folder but nothing at runtime reads them.
