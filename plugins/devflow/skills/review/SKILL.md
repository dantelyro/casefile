---
name: review
description: >
  Use when a finished change needs checking against its spec rules, plan task or issue, or a
  verdict before it is merged — a branch, PR, commit range, a task from a plan in docs/plans/,
  or a bug fix for an issue in docs/issues/. An isolated
  devflow:reviewer agent checks the change against its task or issue and the project's spec rules,
  re-runs the tests itself, and returns approve or changes-requested with findings. Triggers on:
  "review this branch/task/fix before I merge", "is T3 ready to merge", "check the implementer's
  work", "does this change meet the spec". Not for a general read of the current diff for bugs
  with no plan, issue or spec to judge it against: that is the built-in code-review.
---

# Review

A verdict on one change, from an agent that did not write it, cannot edit it, and re-runs its
tests. The main session never reviews the diff itself: reading a diff in the conversation that
produced it is how a change gets approved by the reasoning that wrote it.

## Steps

1. **Resolve the target** to a branch or commit range: a branch name, a PR (`gh pr view <n>
   --json headRefName`), a commit, or "the current branch" (`git merge-base <default> HEAD`..HEAD).
   Note the plan task or issue it implements, and the implementer's report if there is one. Ask
   when the target is ambiguous; do not guess which branch.
2. **Project settings.** Read `.claude/devflow.json`. If it does not exist, propose one — the
   default branch, each app's folder with its `test` and `install` commands as found in the
   project files, its `lint` command when the app has a linter, and the protected paths — and with it `"worktree": { "baseRef": "head" }` in
   `.claude/settings.json` (merged into what is there), so agent worktrees start from local HEAD
   instead of the remote, which misses every unpushed commit (D-040). When the project's frontend
   and backend are separate repositories, also `repo` (this one's name) and `siblings` (each
   other's name and relative path), and `permissions.additionalDirectories` listing those paths so
   this session can read them (D-041). Show both, and **wait** for
   the developer's yes before writing them. Without them, the reviewer still runs, finding test
   commands itself.
   Whether or not the file exists, propose whatever is missing of the following, under the same yes
   when there is one (D-042):
   - **The base branch.** No `default_branch` → ask which local branch work starts from and merges
     back to (`main`, `develop`, `staging`…). Never assume `main`.
   - **Worktrees ignored.** Claude Code puts agent worktrees in `.claude/worktrees/`, each a full
     copy of the project: `.gitignore` and the ignores of every linter, formatter and test runner
     configured at the root (`eslint.config.js`, `.prettierignore`, `vitest.config.ts`…) must list
     it. Unignored, `eslint .` sweeps the copies and can hang.
   - **A linter, per app without one.** Name the usual one for its stack. A no is final: lint is
     optional, tests are not. An app with no test command is asked for one.
3. **Check the tests can run.** For every app the change touches, the tools its test command needs
   must be running, not just installed: Docker's daemon (`docker info`), a database container the
   suite expects. If one is down, tell the developer before dispatching — a reviewer that cannot
   run the tests cannot approve.
4. **Task evals and dispatch.** For a task or issue, obtain results for the target commit through
   [`${CLAUDE_PLUGIN_ROOT}/shared/task-evals.md`](../../shared/task-evals.md). Then dispatch
   `devflow:reviewer` with paths and IDs, not file contents: the target, the plan task or issue
   path, the implementer's report verbatim and those results (or `evals: none applicable`).
5. **Report** the verdict as a short table: what was checked, which test commands ran and their
   counts, findings by severity (blocker, major, minor) with file and line. Say plainly whether the
   change can be merged.

## Never

- **Never merge, fix or commit** from this skill. Fixes go back to whoever wrote the change;
  merging needs the developer's explicit yes, change by change.
- **Never approve on the reviewer's behalf** when it could not run the tests, or soften a finding
  in the summary.
- **Never review by reading the diff yourself** instead of dispatching: the point is a second,
  isolated judgement.

## After the verdict

- `changes-requested`: the findings go back to the implementer, who fixes blocker and major ones in
  a new commit; then review again. Two rounds without approval: stop and show the developer.
- `approve`: tell the developer the change is ready and what minor findings remain; merging is
  their call.
