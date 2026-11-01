# casefile

A Claude Code plugin marketplace and the single plugin it ships: skills, agents and hooks that take a
project from specs to reviewed code, on a branch the developer merges. How the repository is laid out is in `CLAUDE.md`; why,
in `docs/decisions/`.

## Build order

Releases shipped through 0.19.1 predate these specs; the designs of 0.12.0–0.16.0 are in
`docs/specs/history/`, and the later ones are recorded only in their commits and decisions.

- **M1 — The reviewer runs the breaks** (0.20.0): GUARD-001, GUARD-002, GUARD-003, GUARD-004,
  GUARD-005, REV-001, REV-002, REV-003, REV-004, REV-005, REV-006, REV-007, REV-008, IMPL-001, IMPL-002.
- **M2 — Ruff and pytest** (0.21.0): TOOL-004; the tooling itself is a decision, not rules.
- **M3 — Rules and tests** (0.22.0): RULE-001, RULE-002, RULE-003, RULE-004, RULE-005, RULE-006.
- **M7 — Agents that know the project's history** (0.27.0): PLAN-001, PLAN-002, PLAN-003, PLAN-004,
  IMPL-003, IMPL-004, REV-009, REV-010.
- **M8 — Refactor existing code** (later): not specified yet; its questions are in
  `open-questions.md`.
- **M11 — One commit per task, no worktrees** (0.28.0): GUARD-001, GUARD-002, GUARD-005, GUARD-008,
  REV-005, REV-011, IMPL-005, PLAN-005, ORCH-003, ORCH-004, ORCH-005, ORCH-006, ORCH-007, ORCH-008,
  ORCH-009, ORCH-010, ORCH-011, ORCH-012, ORCH-013. Built before M9 and M10.
- **M9 — Lint at the end of each turn** (0.29.0): PRAC-010, PRAC-011, PRAC-012.
- **M10 — The code-practices skill** (0.30.0): PRAC-001, PRAC-002, PRAC-003, PRAC-004, PRAC-005,
  PRAC-006, PRAC-007, PRAC-008, PRAC-009.
