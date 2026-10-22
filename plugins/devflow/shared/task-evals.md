# Main-session task evals

Before dispatching a review for a committed task or issue, read its `Test first`/eval cases and
rule IDs. Use the named cases, or rule-named directories under the project's plugin's `evals/`.
No applicable evals → tell the reviewer `evals: none applicable`; do not invent a required run.

Reuse results only when they identify the same commit and cases. Otherwise the **main session**
runs each task-specific case or glob once on the committed task's worktree, never through an agent:

For a standalone review with no task worktree, create a temporary linked worktree at the exact
target commit for this check; leave existing agent worktrees alone.

```bash
timeout 900 claude plugin eval <plugin-path> --case '<task-case-glob>' --ablation none --runs 2 --max-cost-usd 2 --no-publish --scaffold
```

Use the plugin under test in that worktree, not the installed plugin or another branch. Record
the commit, case names, passed/runs, cost and whether the run was partial. A cap-stopped or partial
run is `unfinished (cap)`, never passed; a failure is a blocker. Claude Code refuses the eval CLI
inside agents' worktrees when an agent invokes it; agents report the handoff instead. Commits and
CI never run evals.

A case granting Bash or PowerShell needs macOS, Linux or WSL2. On native Windows report
`not run (shell sandbox unavailable; run on Fedora)`, never passed. Other missing prerequisites
or explicitly deferred runs are `not run (<reason>)`.

Pass the actual results, including failures and not-run cases, to the reviewer with the task
and implementer report. Missing, failed, unfinished or not-run applicable evals prevent approval;
keep their validation pending. After a new implementer commit, repeat for that commit. The finish
report lists deferred cases and their commands for the developer; case existence is not a pass.
