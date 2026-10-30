# Planner

`casefile:planner` (`agents/planner.md`). Before it plans, it knows what the project decided,
dropped and already built, because it is the last point where a milestone can be stopped before
code is written (see D-065).

### PLAN-001 · The planner reads the project's history before planning      [MANUAL]
Given a milestone to plan
When the planner starts
Then it reads the project's `CLAUDE.md`, `product-decisions.md`, `open-questions.md` and the
decisions index, and in full every decision whose subject or cited rules touch the milestone
And the plan lists the decisions it read on a `History checked:` line under its header.

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
