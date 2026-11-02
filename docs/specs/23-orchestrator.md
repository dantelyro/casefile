# Orchestrator

The main session as it runs `implement` and `fix-bug`: it plans, builds and commits each task itself,
one at a time, with no agent; the reviewer runs only when the developer invokes `review` (see D-074,
D-072).
ORCH-001 and ORCH-002 were used on a branch that was dropped (D-069); ORCH-008 and 009, the wip-ref rules, were removed
with the planner and the implementer (D-074).

### ORCH-003 · One commit per task, made after the developer's yes      [MANUAL]
Given a task or a fix the main session built and checked
When the developer says yes to it
Then it commits the work and the plan's `Status: done` (or the issue's status) in one commit, typed
by the change (`feat`, `fix`, `test`, `refactor`, `docs`…) and naming its rule IDs
And it makes no other commit for that task: none before the work, none for the status.

### ORCH-004 · The work is staged before a review      [MANUAL]
Given uncommitted work in the developer's checkout that the developer asks to have reviewed
When `review` dispatches the reviewer
Then it first runs `git add -A`, so the reviewer's breaks can be restored to the staged copy
(REV-005); no ref is saved.

### ORCH-005 · The checkout is checked after every review      [MANUAL]
Given the reviewer replied
When the orchestrator reads the verdict
Then before anything else it checks the working files against the staged copy; a difference is
restored with `git restore .` and any new untracked file is listed to the developer.

### ORCH-006 · One task at a time      [MANUAL]
Given a milestone or a fix
When it is built
Then one task runs at a time, in the developer's checkout, and there is no parallel mode and no merge
of a task.

### ORCH-007 · A branch is reviewed only from a clean checkout      [MANUAL]
Given a review of a branch that is not checked out
When the developer's checkout has uncommitted changes
Then the orchestrator stops and says what they are; otherwise it switches the checkout to that branch
before dispatching the reviewer.

### ORCH-010 · done needs no commit hash
Given a task with `Status: done`
When `plan_status.py` reads the plan
Then the task is done; `done (<sha>)`, as older plans write it, is read the same way.

### ORCH-011 · The batch is one task
Given a plan with ready tasks
When `plan_status.py` reports the batch
Then it holds only the first ready task, and a `Parallel-safe with:` line is ignored.

### ORCH-012 · A blocked task's status is committed on its own      [MANUAL]
Given a task that becomes blocked
When the main session records it
Then `Status: blocked: <reason>` is committed alone, as `chore(plans): <milestone> <task> blocked`,
and the task's uncommitted work stays in the checkout, listed to the developer.

### ORCH-013 · fixed needs no commit hash
Given an issue whose status is `fixed`, without a hash, because it is committed in the fix's own
commit (ORCH-003)
When `issues_status.py` checks it
Then the fixing commit is the last commit on the current branch that touches the issue file, and the
issue is an error when that commit's copy of the file does not say `fixed`, or when a test it names
is not on the branch; `fixed (<commit>)`, as older issues write it, is checked as before.

### ORCH-014 · casefile ships one agent, the reviewer
Given the plugin
When its files are read
Then `agents/` holds only `reviewer.md`, only the `review` skill dispatches it, and `implement` and
`fix-bug` dispatch no agent; no skill, hook, spec, README, `CLAUDE.md` or manifest names
`casefile:planner` or `casefile:implementer`, and only `docs/decisions/`, `docs/specs/history/` and
`docs/plans/` record them.

### ORCH-015 · implement plans the milestone in the main session      [MANUAL]
Given a milestone to build with no plan yet
When `implement` plans it
Then the main session writes `docs/plans/<milestone>.md` itself, after reading the decision index,
every decision touching the milestone's rules or files, the product decisions, the open questions
and the code the work touches
And the plan records what it was checked against; work that brings back something dropped or
contradicts a decision is a blocker; every task names the code it can reuse; a detail no rule states
is a `Planner choice:` the developer accepts or cuts (D-044); and the developer approves the plan
before any task starts.

### ORCH-016 · implement builds each task test-first in the main session      [MANUAL]
Given an approved plan
When the main session builds a task
Then it writes the task's tests first, each named after its rule ID, and runs them to see each fail
on an assertion, or reports `RED: none` when the behaviour already exists; writes the least code that
makes them pass; then cleans up names and duplication with the tests green
And it never weakens a test (deleting, skipping or loosening it), changes only what the task covers,
stops the task as blocked when it would contradict a decision, files a bug found elsewhere as an issue
after the developer agrees, and runs the app's `test` and `lint` commands before asking for the yes
(ORCH-003).

### ORCH-017 · fix-bug fixes an issue in the main session      [MANUAL]
Given an issue in `docs/issues/`
When `fix-bug` fixes it
Then the main session first writes a test that reproduces the bug and fails, then the least fix that
makes it pass, on the issue's `fix/` branch and under ORCH-016's rules, and commits it after the
developer's yes (ORCH-003).
