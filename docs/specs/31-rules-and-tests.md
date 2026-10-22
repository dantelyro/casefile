# Rules and tests

What a rule's tags mean and what gets a test, across `write-specs`, the planner, `implement` and their
scripts (see D-049).

### RULE-001 · A rule heading needs no tag
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
to a question the rule depends on; the tag comes off once it is confirmed. A milestone whose rules are all `[LATER]` or `[VERIFY]` stops
`implement`, which says what each waits on.

### RULE-003 · MANUAL marks what the developer tests and approves
Given a rule that neither a test nor an eval can check (how a screen feels, a live system a run cannot
reach, the developer's own judgement), or a rule the developer marks as critical
When it is specified and its milestone finishes
Then it is tagged `[MANUAL]`, and a critical rule keeps its test or eval as well; the tag is defined
that way in `specs-layout.md` and the specs README; `implement`'s finish report lists those rules as
the developer's checklist, and the milestone is done only after the developer's ok on each; `[VERIFY]`
rules waiting on the developer's answer are listed under what the developer decides next. Claude may
suggest a rule is critical, and it is tagged only on the developer's yes. See D-053.

### RULE-004 · Tests cover what the project's code does      [MANUAL]
Given a rule in a milestone
When the planner plans it
Then it plans a test named after the rule when the rule describes something the project's own code
does: the test proves the code does what the rule says and fails when it stops, covering the rule's
normal case, its edge cases and its failure cases. A rule that describes anything else gets no test,
with its reason (RULE-005). The method in the specs layout and the specs README says a failing test
comes first only for a rule that describes what the project's code does.

### RULE-005 · A rule without a test carries its reason      [MANUAL]
Given a rule in a plan's scope that gets no test
When the planner lists it under `## Rules covered`
Then its line states why, e.g. `- TOOL-004 → T4` for a tested rule and
`- REV-001 → T4 (no test: agent prose, checked by hand)` for an untested one. A task the plan marks
`Test first: none (no test: …)` is not a missing-test finding.

### RULE-006 · rules_coverage flags a rule with neither a test nor a reason
Given a rule in a plan's scope that is not `[LATER]`, `[VERIFY]` or `[MANUAL]`
When `rules_coverage.py` runs
Then the rule is covered when a test is named after it, reasoned when its plan line states a reason
in `(no test: …)`, and missing otherwise, with exit 1.

### RULE-007 · A skill's or agent's behaviour is tested by an eval named after the rule
Given a rule that describes what a skill or agent does
When the planner plans it
Then it plans an eval at `evals/<RULE-ID>-<slug>/` whose grader checks what shows the rule held: a file
the run wrote, its final reply, or its tool calls. See D-053.

### RULE-008 · rules_coverage counts an eval as a rule's test
Given an eval directory named `<RULE-ID>-<slug>` under `evals/`
When `rules_coverage.py` runs
Then that rule is covered, as if a test were named after it.

### RULE-009 · Evals run once per task, under a cost cap
Given a task whose rules have evals
When the implementer has committed it
Then the main session runs the task's evals on the task's worktree with `--ablation none --runs 2
--max-cost-usd 2` and hands the result to the reviewer, who judges it with the change; a run the cap
stopped is reported as unfinished, never as passed; commits and CI never run evals. Agents do not run
evals: Claude Code refuses `claude plugin eval` inside an agent's worktree. See D-053.
