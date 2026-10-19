# `implement` — from specs to merged code — design

**Date:** 2026-10-14.
**Status:** Approved 2026-10-14. Not yet implemented.
**Release:** `0.15.0`. Needs `0.13.0` (hooks, reviewer) and `0.14.0` (implementer, issues, merge
procedure). The specs it reads come from `write-specs` (`2026-10-14-write-specs-design.md`, 0.16.0)
or are written by hand — the pilot project's were. `mvp` and `project-specs` are already gone
(`2026-10-14-remove-mvp-and-project-specs-design.md`, 0.12.0).

## Summary

`implement` is the pilot project milestone workflow, generalised to any **scope**: a milestone of a new
project, or one feature in an existing one. It plans the scope as small test-first tasks, implements
them in parallel worktrees, reviews each, and merges each after the developer says yes. It never
writes specs: it starts from rules that already exist.

| Piece | What it is |
|---|---|
| `implement` skill | The orchestrator. Never writes product code, tests or specs itself. |
| `devflow:planner` agent | Turns one scope into an ordered task list tied to rule IDs. Writes only the plan file. |
| Plan file | The single source of truth for the scope's progress: `<plans_dir>/<scope>.md`. |
| Planner guard rules | The `planner` row of the guard table in the 0.13.0 spec, now enforced. |

## Input: rules with IDs

`implement` needs specs where each behaviour is a heading with a stable ID and a tag:

```
### MATCH-010 · Formula     [MVP]
```

`[MVP]` is planned, `[LATER]` is not, `[VERIFY]` is flagged as a blocker instead of planned around a
guess; `[MANUAL]` is checked in review, not by a test. Every test is named after its rule ID, which is
what lets the reviewer check rule by rule and the finish report list each rule with or without a
passing test. The default layout is the pilot project's, written by `write-specs`: `docs/specs/NN-area.md` and
milestones in the "Build order" section of `docs/product/blueprint.html`. `specs_dir` in
`.claude/devflow.json` can point elsewhere; the heading format is the only hard requirement. The scope
is always a milestone in the build order — a feature gets its own milestone there.

No rules for the request → stop and point the developer to `write-specs`. **A spec gap found later
is asked, never invented**: the builder gets an exact rule after the developer decides (the pilot project M1/T3
failed twice on an invented heuristic).

## The flow

### 1. Plan

`devflow:planner` writes `<plans_dir>/<scope>.md`: ordered tasks, each with rules, test names written
first, files, a "Done when" check, dependencies, "parallel-safe with" and notes; plus "Rules covered"
and "Blockers". The developer approves the plan and its blockers before any implementation, and the
approved plan is committed.

### 2. Implement, review, merge

The loop from the pilot project's `build-milestone`:

1. **Batch:** ready tasks (todo, dependencies done, no open blocking issue), the first plus its
   parallel-safe peers, at most 3.
2. **Implement in parallel:** one `devflow:implementer` per task, dispatched in one message.
3. **Review each:** `devflow:reviewer` with the plan path, task ID and the implementer's report.
4. **Fix loop:** at most 2 rounds per task, through the same implementer.
5. **Merge:** the shared merge procedure (0.14.0 spec), per task, after the developer's yes.
6. **Resume:** a task left `in-progress` by an earlier session — check its branch for a finished,
   unreviewed commit and offer to review it before discarding anything.

### 3. Bugs found along the way

Bugs never ride along in a feature task's branch. Each becomes a file in `docs/issues/` (format in
the 0.14.0 spec) and is fixed by `fix-bug` on its own branch:

- **Unrelated to the scope** → the issue is filed, the scope continues. Fixing it inside a feature
  branch would mix two unrelated changes in one review and one merge.
- **Related, and blocking a task** (the bug is in already-merged work the next task builds on) → the
  issue names the task it blocks; that task is not batched until the issue is fixed and merged. The
  fix is merged first, then the task proceeds on top of it.
- **In the task's own unmerged branch** → not an issue: it is a review finding, fixed in the fix loop.

Agents report bugs in their `NOTES`; the orchestrator files the issue after the developer agrees.

### 4. Finish

Report tasks done and blocked, issues opened and fixed during the scope, every rule in scope with
whether a passing test exists, and what to decide next.

## Scripted steps

Mechanical steps are scripts, not prose (0.13.0 principle), standard library only, tested:

| Script | Replaces judgement on |
|---|---|
| `plan_status.py <plan>` | which tasks are ready, the next batch, tasks stuck `in-progress`, tasks waiting on an open issue |
| `rules_coverage.py <scope>` | which rules in scope have a test named after them, and whether it passed in the last run |

## Decisions to record when implemented

- **D-034** — Rules with IDs are the unit of specification, testing and review.
- **D-035** — The orchestrator never writes product code, tests or specs; the plan file is the progress record.

D-033 (issues and `Blocks:`) is recorded with `fix-bug` in 0.14.0; this release only reads it.
