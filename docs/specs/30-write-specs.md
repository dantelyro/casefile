# write-specs

The `write-specs` skill (`skills/write-specs/`). Rules here cover specifying code that already exists
(see D-046); the rest is in `history/2026-10-14-write-specs-design.md`.

### SPEC-001 · Rules are drafted from existing code      [MANUAL]
Given the developer names existing code to specify ("spec the existing login flow")
When `write-specs` drafts
Then it reads the code in that scope and drafts one rule per behaviour it observes, in the usual
format and area files, each with a new ID.

### SPEC-002 · Every rule drafted from code is proposed      [MANUAL]
Given a rule drafted from existing code
When the draft is shown
Then the rule is marked proposed: code shows what a system does, never what it must do, so it
becomes a requirement only at the developer's yes.

### SPEC-003 · Behaviour that looks wrong is asked, never drafted      [MANUAL]
Given existing code whose behaviour looks like a bug
When `write-specs` drafts
Then it drafts no rule for it and asks at the approval step instead; the answer becomes a rule, or an
issue for `fix-bug` after the developer's yes. No test is written to assert it.

### SPEC-004 · The milestone holds tests-only tasks      [MANUAL]
Given the rules drafted from existing code are approved
When their milestone is planned
Then the planner marks each of its tasks tests-only, and the implementer reports them as IMPL-002.

### SPEC-005 · The description triggers on existing code      [MVP]
Given a request to specify code that already exists
When skills are matched
Then `write-specs` triggers, and it does not on a request to fix a bug in that code; checked by trigger
evals (`evals/write-specs-*`, `evals/not-write-specs-*`).
