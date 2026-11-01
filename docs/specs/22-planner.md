# Planner

`casefile:planner` (`agents/planner.md`). Before it plans, it knows what the project decided,
dropped and already built, because it is the last point where a milestone can be stopped before
code is written (see D-065).

### PLAN-001 · The plan records the history it was checked against      [MANUAL]
Given a milestone to plan, with the project context every agent starts with (CTX-001)
When the planner writes the plan
Then the plan lists, on a `History checked:` line under its header, every decision it read in full
because its subject or cited rules touch the milestone, and each product document it read or found
absent.

### PLAN-002 · Work that brings back something dropped is a blocker      [MANUAL]
Given a rule or task that would bring back something dropped, reverted or superseded — a decision
entry with that status, or a product decision marked dropped
When the planner plans the milestone
Then it does not plan that work: it lists it under Blockers, naming the decision and the reason it
was dropped, until the developer rules
And when the developer brings it back, a new decision entry supersedes the old one.

### PLAN-003 · Work that contradicts a decision is a blocker      [MANUAL]
Given a rule or task that contradicts an accepted decision entry or a product decision
When the planner plans the milestone
Then it lists the contradiction under Blockers, naming both, and plans nothing around a guess.

### PLAN-004 · Every task names the code it can reuse      [MANUAL]
Given a task in the plan
When the planner writes it
Then it searches the code for functions, components, types, fixtures and tests the task can use,
and the task has a `Reuse:` line naming each by file and symbol, or `Reuse: none found (searched:
<terms>)`.

### PLAN-005 · Tasks carry no Parallel-safe line      [MANUAL]
Given a milestone to plan
When the planner writes a task
Then the task has no `Parallel-safe with:` line: tasks are built one at a time. See D-072.
