# D-069 — Committing a task's status by amending the task's commit is dropped as a workaround

**Status:** Accepted (2026-11-01).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-01, in the developer's words quoted above

**Context:** implement commits the plan only to change a task's Status (in-progress before dispatch; done after acceptance in task-by-task mode), which the developer called dirt in the git log. A fix was built on fix/task-status-commits (3705882): statuses left uncommitted, done amended into the task's own commit, plan_status.py accepting a plain done (ORCH-001, ORCH-002). The developer: 'that looks like a workaround'. The cause is that status lives in a tracked file separate from the work, so every variant that keeps a Status line must commit it somehow; the amend also changes the hash the reviewer approved.

**Options:** (a) merge the amend fix; (b) drop it and replace it later with status read from git: every task lands by a merge commit, plan_status.py derives done from merge(<milestone>/<task>) commits and in progress from task branches; (c) keep the status commits.

**Decision:** (b): dropped unmerged, the branch deleted, on the developer's choice 'Drop it'. The git-based design is an open question for the cleanup the developer is starting, not decided here. The status commits stay until then.

**Trade-offs:** Status-only commits remain in implement for now. ORCH-001 and ORCH-002 and the fix's decision entry never reached main; this entry is their only record.
