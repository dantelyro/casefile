# Orchestrator

The session that runs `implement`, `fix-bug` and `review`, or builds a task itself. It is the only one
that commits: once per task or fix, after review, with no worktrees and no parallel tasks (see D-072).
ORCH-001 and ORCH-002 were used on a branch that was dropped (D-069); numbering starts at 003.

### ORCH-003 · One commit per task, made after approval      [MANUAL]
Given a task or a fix the reviewer approved, and the developer's yes
When the orchestrator accepts it
Then it commits the staged work and the plan's `Status: done` (or the issue's status) in one commit,
typed by the change (`feat`, `fix`, `test`, `refactor`, `docs`…) and naming its rule IDs
And it makes no other commit for that task: none before dispatch, none for a review round, none for
the status. A task the orchestrator builds itself is committed the same way.

### ORCH-004 · The work is staged and saved before each review      [MANUAL]
Given the implementer reported a task or a fix round done
When the orchestrator sends it to the reviewer
Then it first runs `git add -A` and saves the staged tree as a commit under
`refs/casefile/wip/<milestone>/<task>` (`refs/casefile/wip/issues/<number>` for a fix), replacing the
previous round's, and deletes that ref once the task is committed.

### ORCH-005 · The checkout is checked after every review      [MANUAL]
Given the reviewer replied
When the orchestrator reads the verdict
Then before anything else it checks the working files against the staged copy; a difference is
restored with `git restore .` and any new untracked file is listed to the developer.

### ORCH-006 · One task at a time, without worktrees      [MANUAL]
Given a milestone or a fix
When it is built
Then one task runs at a time, the implementer and the reviewer are dispatched without a worktree, and
there is no parallel mode and no merge of a task.

### ORCH-007 · A branch is reviewed only from a clean checkout      [MANUAL]
Given a review of a branch that is not checked out
When the developer's checkout has uncommitted changes
Then the orchestrator stops and says what they are; otherwise it switches the checkout to that branch
before dispatching the reviewer.

### ORCH-008 · An abandoned task is discarded; a resumed one is restored      [MANUAL]
Given a task the developer abandons, or a session resuming a milestone
When the task has a wip ref (ORCH-004)
Then an abandoned task's work is discarded after the developer's yes and its ref deleted; a resumed
task's work is restored from its ref when the checkout no longer holds it.

### ORCH-009 · A task is in progress while its wip ref exists
Given a plan whose task has `Status: todo`
When `refs/casefile/wip/<milestone>/<task>` exists
Then `plan_status.py` reports the task in progress and leaves it out of the batch; the plan never
holds `in-progress`.

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
When the orchestrator records it
Then `Status: blocked: <reason>` is committed alone, as `chore(plans): <milestone> <task> blocked`,
and the task's uncommitted work is kept under its wip ref.
