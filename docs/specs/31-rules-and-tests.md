# Rules and tests

What a rule's tags mean and what gets a test, across `write-specs`, the planner, `implement` and their
scripts (see D-049). Until this milestone ships, devflow's lint still requires a tag, so the rules
below that are untagged in meaning carry `[MVP]`; RULE-001 removes it from every rule.

### RULE-001 · A rule heading needs no tag      [MVP]
Given a rule heading in the specs
When `spec_lint.py` checks it
Then `### ID · Title` with no tag passes; the allowed tags are `[LATER]`, `[VERIFY]` and `[MANUAL]`,
and `[MVP]` is an error that says to remove the tag. No rule in `docs/specs/` carries `[MVP]`.

### RULE-002 · Every rule in a milestone is planned unless it waits      [MANUAL]
Given a milestone's rules
When the planner and `implement` take its scope
Then every rule in it is planned except `[LATER]` and `[VERIFY]` ones; `implement` no longer requires
`[MVP]` headings, and `write-specs` never writes `[MVP]`. `[VERIFY]` marks a rule that waits for
something to be confirmed before it is built: a fact about an outside system, or the developer's answer
to a question the rule depends on; the tag comes off once it is confirmed.

### RULE-003 · [MANUAL] is the developer's to test by hand      [MANUAL]
Given a rule the AI has no way to test (an agent's or skill's behaviour, a live run, how a screen
feels)
When it is specified and its milestone finishes
Then it is tagged `[MANUAL]`, the tag is defined that way in `specs-layout.md` and the specs README,
and `implement`'s finish report lists those rules as the developer's checklist.

### RULE-004 · Tests cover what the project's code does      [MANUAL]
Given a rule in a milestone
When the planner plans it
Then it plans a test named after the rule when the rule describes something the project's own code
does: the test proves the code does what the rule says and fails when it stops, covering the rule's
normal case, its edge cases and its failure cases. A rule that describes anything else gets no test,
with its reason (RULE-005).

### RULE-005 · A rule without a test carries its reason      [MANUAL]
Given a rule in a plan's scope that gets no test
When the planner lists it under `## Rules covered`
Then its line states why, e.g. `- TOOL-004 → T4` for a tested rule and
`- REV-001 → T4 (no test: agent prose, checked by hand)` for an untested one.

### RULE-006 · rules_coverage flags a rule with neither a test nor a reason      [MVP]
Given a rule in a plan's scope that is not `[LATER]`, `[VERIFY]` or `[MANUAL]`
When `rules_coverage.py` runs
Then the rule is covered when a test is named after it, reasoned when its plan line states a reason
in `(no test: …)`, and missing otherwise, with exit 1.
