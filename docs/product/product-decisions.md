# Product decisions

- devflow is specified in its own `write-specs` layout, built milestone by milestone with `implement`;
  earlier designs stay in `docs/specs/history/` (2026-10-19), see D-047
- The reviewer, not the implementer, proves tests can fail (2026-10-19) → REV-001, IMPL-001, see D-045
- Tests for existing code go through `write-specs` and `implement`, with no separate skill
  (2026-10-19) → SPEC-001, see D-046
- Documents are brought into devflow's layout by a separate skill, not by hand and not by the
  evidence skill (2026-10-19) → DOCS-001
- The repo adopts ruff and pytest, run through uv, as the milestone right after M1, ahead of specs for existing code
  (2026-10-19) → TOOL-004, see D-048
- The test suite is rewritten in pytest's style, not only run by pytest (2026-10-19), see D-048
- Every ruff finding is fixed in the code, with ruff's default rules (2026-10-19), see D-048
- ruff and pytest are uv dev dependencies in `pyproject.toml`, with `uv.lock` committed (2026-10-19), see D-048
- devflow drops the `[MVP]` tag and adds no test tag: what gets a test follows from the project's own
  behaviour, never tools, config or prose; `[MANUAL]` means the developer tests it by hand because the
  AI cannot; `rules_coverage.py` flags a rule with neither a test nor a stated reason (2026-10-20)
  → RULE-001..006, see D-049
- Development tooling is not a spec rule: ruff, pytest, uv and the commit gate are recorded in decisions
  (D-048) and CLAUDE.md, and M2's four tooling rules leave the specs (2026-10-20); TOOL-004 stays,
  because shipped code being standard library is what users rely on
