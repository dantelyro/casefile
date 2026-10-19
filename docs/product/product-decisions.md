# Product decisions

- devflow is specified in its own `write-specs` layout, built milestone by milestone with `implement`;
  earlier designs stay in `docs/specs/history/` (2026-10-19), see D-047
- The reviewer, not the implementer, proves tests can fail (2026-10-19) → REV-001, IMPL-001, see D-045
- Tests for existing code go through `write-specs` and `implement`, with no separate skill
  (2026-10-19) → SPEC-001, see D-046
