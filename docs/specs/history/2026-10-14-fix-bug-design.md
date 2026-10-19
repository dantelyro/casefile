# `fix-bug`, issues and the implementer — design

**Date:** 2026-10-14.
**Status:** Approved 2026-10-14. Not yet implemented.
**Release:** `0.14.0`. Needs `0.13.0` (`2026-10-14-review-design.md`): the hook runtime, the guard
rules, `.claude/devflow.json` and the reviewer.

## Summary

| Piece | What it is |
|---|---|
| `docs/issues/` | One file per bug. Where every bug is recorded, whether found by the developer, an agent, or during a feature. |
| `devflow:implementer` agent | Does one task in its own worktree, test-first, and commits it on that worktree's branch. Never merges. |
| `fix-bug` skill | Takes an issue, has the implementer reproduce it with a failing test and fix it, has the reviewer check it, and merges after the developer approves. |
| `shared/merge.md` | The merge procedure, used by `fix-bug` and `implement`. |
| Implementer guard rules | The `implementer` row of the guard table in the 0.13.0 spec, now enforced. |

Bug fixing ships before `implement` because it is the same loop with one task and no planner.

## Issues

### Why a folder, not tasks in the feature's plan

A bug found while building a feature is fixed **on its own branch**, never inside the feature's:

1. **Unrelated to the feature** — fixing it in the feature branch mixes two unrelated changes into one
   review and one merge. It is filed and the feature continues.
2. **Related, and blocking** — the feature cannot proceed until it is fixed (the bug is in merged work
   the next task builds on). It is still its own fix on its own branch, merged first, and its issue
   **points to the task it blocks**. That task waits until the issue is fixed.

A bug inside a task's own unmerged branch is not an issue: it is a review finding for that task.

### Format

`docs/issues/NNNN-kebab-slug.md`, numbered like the decision log (highest file is the next id):

```
# I-0007 — Web image fails to build with nested test files

- Status: open | in-progress | fixed (<implementer commit>) | wontfix: <reason>
- Found: 2026-10-14, during docs/plans/M1.md T11      (or: reported by the developer)
- Blocks: docs/plans/M1.md T13                         (or: none)
- Related to: docs/plans/M1.md T8                      (the work it was found in, or: none)
- Rules: ARCH-001

## What happens
## What should happen
## How to see it
## Test that must fail first
```

- `Blocks` is what makes case 2 enforceable: `implement`'s `plan_status.py` reads it and keeps the
  blocked task out of every batch until the issue is `fixed`.
- `Status` changes to `fixed (<implementer commit>)` only inside the merge commit, after the tests
  pass on the default branch — never on a branch that was not merged. (Planned as the merge commit's
  own id, which a commit cannot contain; the implementer's commit is on the default branch once
  merged, as the pilot project's plans record it.)

### `issues_status.py`

Whether an issue was really fixed is checked, not read off its status line. `skills/fix-bug/scripts/issues_status.py` (standard
library only, tested in the 0.13.0 suite):

- lists every `open` and `in-progress` issue, and the task each one blocks;
- for every `fixed (<commit>)` issue, checks that the commit exists on the default branch and that
  the test named under "Test that must fail first" exists on it. (Planned as "and passed in the last
  run"; devflow keeps no record of test runs, so passing is shown where it happens — the merge
  procedure runs the suite before every merge commit.)
- gives the next free issue id (`--next-id`) and the open issues blocking a task (`--blocks`);
- reports a `fixed` issue that fails either check as an error, and exits non-zero.

`fix-bug` runs it after each merge, and `implement` runs it before picking each batch.
- The folder is created only after the developer agrees, the first time an issue is filed.
- Agents never write issues; they report bugs in their `NOTES`, and the main session files them after
  the developer says yes. `docs/issues/` is added to every agent's protected paths by default.

## The `fix-bug` flow

1. **The issue.** From an existing `docs/issues/` file, or written now from the developer's report
   (what happens, what should happen, how to see it, the test that must fail first).
2. **Implement.** Dispatch `devflow:implementer` with the issue path.
3. **Review.** Dispatch `devflow:reviewer` with the issue path and the implementer's report.
4. **Fix loop.** `changes-requested` → the same implementer (continued, so it keeps its worktree)
   fixes blocker and major findings in a **new** commit. At most 2 rounds, then stop and show the
   developer.
5. **Merge** (`shared/merge.md`) after the developer says yes; the issue's status becomes
   `fixed (<implementer commit>)` in the merge commit.

## The implementer agent

`agents/implementer.md`, from the pilot project's with the M1 lessons, generalised. It serves both `fix-bug`
(input: an issue) and `implement` (input: a plan task).

- **Red → green → refactor.** The test fails for the right reason before any fix.
- **Every planned item and note is part of the task.** Each is done, or listed in the report's
  `NOT DONE:` line with the reason. A silently skipped item is a failed task.
- **Bugs elsewhere are reported, not fixed:** in `NOTES`, with enough detail to file an issue.
- **Never** edits the protected paths, `.claude/` or other worktrees; never merges or pushes
  (enforced by hooks, stated so the agent does not waste attempts).
- **Dependencies are added with the package manager's command** (`npm install x`, `uv add x`), never by
  typing a version into a manifest — the developer's rule, carried over from `project-specs` (D-026).
- A fresh database or service for a check is a **throwaway** one (own container, own port), removed
  afterwards; never the developer's.
- Report block: `STATUS`, `TASK`, `BRANCH`, `COMMIT`, `RULES`, `TESTS` (per app: files and counts,
  unit and integration separately), `FILES`, `NOTES`, `NOT DONE`.
- `model: sonnet`, `isolation: worktree`.

## `shared/merge.md`

A top-level `shared/` folder holds instructions more than one skill uses, so no skill owns another's
procedure. Each skill links it directly from its `SKILL.md` (references never nest, D-024). On the
default branch, after the developer's explicit yes:

1. Working tree clean, on the default branch.
2. `git merge --no-ff --no-commit <branch>`.
3. Run the configured test command of every app the change touched; if it touched a container
   definition or an app folder, rebuild that image. Failure → `git merge --abort`, report.
4. Commit `merge(<scope>): <title> [<rule IDs>]`, updating the task's or issue's status in the same
   commit. Minor findings merged unfixed are written down where the task or issue lives, as
   "accepted at merge".
5. Clean up the implementer's and every reviewer's worktree and branch. **Before** removing a worktree,
   run each app's configured cleanup (for example a per-checkout test database drop). Never `--force`
   without the developer's yes.

`.claude/devflow.json` gains `apps.<name>.cleanup` and `apps.<name>.image` for steps 3 and 5.

## Worktree facts that shape this

- A plugin agent's worktree branches from the **default branch**, not the session's `HEAD`. Merges
  happen on the default branch, so the next task starts from merged work — and a blocking fix, once
  merged, is under the task it unblocks.
- Untracked dependencies (`node_modules`, virtualenvs) are not in a new worktree. The agent installs
  from the lock file with the app's configured `install` command; the reviewer may do the same.
- An agent cannot commit in another agent's worktree. Resuming an interrupted task means reviewing its
  existing commit; fixes come from a new implementer in its own worktree, or from the main session
  with the developer's yes.
- Shared services (one database, one port) collide between worktrees. Projects should give each
  checkout its own test database (the pilot project M1/F3). `[VERIFY]` whether this can be detected generally;
  the first version only warns from config.

## Decisions to record when implemented

- **D-031** — Merging is the main session's job, after the developer's explicit yes per change; agents
  never merge.
- **D-032** — Instructions used by more than one skill live in `shared/`, linked directly from each
  skill that uses them.
- **D-033** — Bugs are issues in `docs/issues/`, fixed on their own branch; a bug that blocks a task
  blocks it by reference (`Blocks:`), never by sharing its branch.
