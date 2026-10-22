# write-specs

The `write-specs` skill (`skills/write-specs/`). Rules here cover specifying code that already exists
(see D-046) and how product decisions are recorded (see D-051); the rest is in
`history/2026-10-14-write-specs-design.md`.

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

### SPEC-005 · The description triggers on existing code      [MANUAL]
Given a request to specify code that already exists
When skills are matched
Then `write-specs` triggers, and it does not on a request to fix a bug in that code; checked by trigger
evals (`evals/write-specs-*`, `evals/not-write-specs-*`).

### SPEC-006 · An inferred product decision is asked on its own
Given a product decision `write-specs` inferred rather than read from the developer's own words
When the draft is shown for approval
Then it is asked as its own yes-or-no question; a yes writes it with ✅, a no writes it with ❌, and no
answer leaves it in `open-questions.md`. The developer's yes to the whole draft never covers it:
nothing is accepted by silence. See D-051.

### SPEC-007 · product-decisions.md opens with a legend naming the developer
Given `write-specs` creates `docs/product/product-decisions.md`
When the file is written
Then the first line under its heading is `✅ decided by <name> · ❌ rejected by <name>`, with `<name>`
taken from `git config user.name`, and every line starts with ✅ or ❌. See D-051.

### SPEC-008 · spec_lint flags a product decision without its icon
Given `docs/product/product-decisions.md` exists
When `spec_lint.py` runs
Then a `- ` line that does not start with `- ✅ ` or `- ❌ ` is an error naming the line, and so is a
file without the legend line.
