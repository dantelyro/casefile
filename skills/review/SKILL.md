---
name: review
description: >
  Use when a finished change needs checking against its spec rules, plan task or issue, or a
  verdict before it is merged — a branch, PR, commit range, a task from a plan in docs/plans/,
  or a bug fix for an issue in docs/issues/. An isolated
  casefile:reviewer agent checks the change against its task or issue and the project's spec rules,
  re-runs the tests itself, and returns approve or changes-requested with findings. Triggers on:
  "review this branch/task/fix before I merge", "is T3 ready to merge", "review what you just
  built", "does this change meet the spec". Not for a general read of the current diff for bugs
  with no plan, issue or spec to judge it against: that is the built-in code-review.
---

# Review

A verdict on one change, from an agent that did not write it, cannot edit it, and re-runs its
tests. The main session never reviews the diff itself: reading a diff in the conversation that
produced it is how a change gets approved by the reasoning that wrote it.

## Steps

1. **Resolve the target** to a branch or commit range: a branch name, a PR (`gh pr view <n>
   --json headRefName`), a commit, or "the current branch" (`git merge-base <default> HEAD`..HEAD).
   Note the plan task or issue it implements, and the author's report if there is one. Ask
   when the target is ambiguous.
2. **Project settings.** Read `.claude/casefile.json`. If it does not exist, propose one — the
   default branch, each app's folder with its `test` and `install` commands as found in the
   project files, its `lint` command when the app has a linter, and the protected paths. When the project's frontend
   and backend are separate repositories, also `repo` (this one's name) and `siblings` (each
   other's name and relative path), and `permissions.additionalDirectories` listing those paths so
   this session can read them (D-041). Show both, and **wait** for
   the developer's yes before writing them. Without them, the reviewer still runs, finding test
   commands itself.
   Whether or not the file exists, propose whatever is missing of the following, under the same yes
   when there is one (D-042):
   - **The base branch.** No `default_branch` → ask which local branch work starts from and merges
     back to (`main`, `develop`, `staging`…). Never assume `main`.
   - **A linter, per app without one.** Name the usual one for its stack. A no is final: lint is
     optional, tests are not. An app with no test command is asked for one.
3. **Check the tests can run.** For every app the change touches, the tools its test command needs
   must be running, not just installed: Docker's daemon (`docker info`), a database container the
   suite expects. If one is down, tell the developer before dispatching — a reviewer that cannot
   run the tests cannot approve.
4. **Check out the target** (ORCH-007). The reviewer works in this checkout and never switches
   branches. A target that is not checked out: `git status --porcelain` not empty →
   stop and tell the developer what is uncommitted; otherwise `git switch <branch>`. A target that is
   the uncommitted work in this checkout: stage it first with `git add -A` (ORCH-004), so each break
   the reviewer makes is restored to that staged copy.
5. **Dispatch `casefile:reviewer`** with paths and IDs, not file contents: the
   target and its base, the plan task or issue path, and the author's report verbatim. When it
   replies, check that the working files match what was checked out or staged (`git diff --quiet`, no untracked
   files from `git ls-files --others --exclude-standard`); otherwise `git restore .` and tell the
   developer about every untracked file left (ORCH-005).
6. **Report** the verdict as a short table: what was checked, which test commands ran and their
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

- `changes-requested`: the findings go back to whoever wrote the change, who fixes blocker and major
  ones; then review again. Two rounds without approval: stop and show the developer.
- `approve`: tell the developer the change is ready and what minor findings remain; merging is
  their call.
