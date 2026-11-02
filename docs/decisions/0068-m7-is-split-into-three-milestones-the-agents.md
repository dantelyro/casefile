# D-068 — M7 is split into three milestones: the agents' history checks, the Stop lint and the code-practices skill

**Status:** Accepted (2026-11-01).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-01, in the developer's words quoted under Context and Decision

**Context:** M7 bundled three pieces of work planned together on 2026-10-29: the planner, implementer and reviewer reading the decision log (PLAN, IMPL-003/004, REV-009/010), a Stop hook that lints what changed during a turn (PRAC-010..012), and the code-practices skill (PRAC-001..009). With the first piece built, the developer: 'you know this milestone is too big with lots of thinks the ai, the code practices, the lint and the skill are all thing on their own'. None depends on another: the Stop hook runs whatever lint command .claude/casefile.json names, and the skill only proposes linter rules.

**Options:** (a) keep M7 whole; (b) M7 keeps the agents' history checks and ships, the Stop lint becomes M9 and the skill M10, M8 (refactor, later) keeps its number; (c) the same split with the skill before the lint.

**Decision:** (b), proposed by the main session and accepted by the developer: 'yes split it that way'. M7 ships as 0.27.0 with PLAN-001..004, IMPL-003/004, REV-009/010; M9 (0.28.0) is PRAC-010..012; M10 (0.29.0) is PRAC-001..009. The lint comes first because a linter rule enforces what prose did not (D-067). The specs are unchanged; the plans carry over the rulings of 2026-10-31.

**Trade-offs:** Three releases instead of one, each with its own docs and version task. M10's reviewer task builds on M7's reviewer changes. The milestone numbers no longer match the build order (M8 sits between M7 and M9 and comes later).

**Changed by:**
- 2026-11-01 · dantelyro — by D-075: M7 was built; M9 and M10, never built, are dropped with their specs.
