# casefile

A Claude Code plugin marketplace and the single plugin it ships: skills, agents and hooks that take a
project from specs to reviewed, merged code. How the repository is laid out is in `CLAUDE.md`; why,
in `docs/decisions/`.

## Build order

Releases shipped through 0.19.1 predate these specs; their designs are in `docs/specs/history/`.

- **M1 — The reviewer runs the breaks** (0.20.0): GUARD-001, GUARD-002, GUARD-003, GUARD-004,
  GUARD-005, REV-001, REV-002, REV-003, REV-004, REV-005, REV-006, REV-007, REV-008, IMPL-001, IMPL-002.
- **M2 — Ruff and pytest** (0.21.0): TOOL-004; the tooling itself is a decision, not rules.
- **M3 — Rules and tests** (0.22.0): RULE-001, RULE-002, RULE-003, RULE-004, RULE-005, RULE-006.
- **M6 — Claim audit** (0.26.0): CLAIM-001, CLAIM-002, CLAIM-003, CLAIM-004, CLAIM-005, CLAIM-006,
  CLAIM-007, CLAIM-008, CLAIM-009, CLAIM-010, CLAIM-011, CLAIM-012.
