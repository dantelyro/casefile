# devflow

A Claude Code plugin marketplace and the single plugin it ships: skills, agents and hooks that take a
project from specs to reviewed, merged code. How the repository is laid out is in `CLAUDE.md`; why,
in `docs/decisions/`.

## Build order

Releases shipped through 0.19.1 predate these specs; their designs are in `docs/specs/history/`.

- **M1 — The reviewer runs the breaks** (0.20.0): GUARD-001, GUARD-002, GUARD-003, GUARD-004,
  GUARD-005, REV-001, REV-002, REV-003, REV-004, REV-005, REV-006, REV-007, REV-008, IMPL-001, IMPL-002.
- **M2 — Specs for existing code** (0.21.0): SPEC-001, SPEC-002, SPEC-003, SPEC-004, SPEC-005.
- **M3 — Docs reconciliation** (later): DOCS-001, DOCS-002, DOCS-003, DOCS-004, DOCS-005,
  DOCS-006, DOCS-007, DOCS-008.
- **M4 — Ruff and pytest** (later): TOOL-001, TOOL-002, TOOL-003, TOOL-004.
