# Product decisions

- devflow is specified in its own `write-specs` layout, built milestone by milestone with `implement`;
  earlier designs stay in `docs/specs/history/` (2026-10-19), see D-047
- The reviewer, not the implementer, proves tests can fail (2026-10-19) → REV-001, IMPL-001, see D-045
- Tests for existing code go through `write-specs` and `implement`, with no separate skill
  (2026-10-19) → SPEC-001, see D-046
- Documents are brought into devflow's layout by a separate skill, not by hand and not by the
  evidence skill (2026-10-19) → DOCS-001
- The repo adopts ruff and pytest, run through uv, as their own milestone after M3 (2026-10-19)
  → TOOL-001..005
- The test suite is rewritten in pytest's style, not only run by pytest (2026-10-19) → TOOL-003, see D-048
- Every ruff finding is fixed in the code, with ruff's default rules (2026-10-19) → TOOL-001
- ruff and pytest are uv dev dependencies in `pyproject.toml`, with `uv.lock` committed (2026-10-19)
  → TOOL-002, TOOL-005, see D-048
