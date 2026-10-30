---
name: implement
description: >
  Use when a milestone of spec rules is to be built: its plan written by casefile:planner, then its
  tasks built on a feat/ branch by casefile:implementer — one by one, or in parallel worktrees — each
  reviewed by casefile:reviewer and accepted after the developer says yes, until the milestone is
  done; the developer merges the branch. Resumes a milestone from its plan in
  docs/plans/. Triggers on: "build M2", "implement milestone M3", "build the saved-jobs feature from
  its specs", "continue the milestone", "what's left in M2". Not for one bug (fix-bug), not for
  reviewing one change (review), and not for writing the specs a milestone needs.
---

# Implement a milestone

You are the **orchestrator**. You coordinate agents and keep the plan; you never write product code,
tests or specs yourself. The specs define correct behaviour; the plan file is the single record of
progress.

Scripts below run as `<python> "${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<name>.py"`, where
`<python>` is `py -3` on Windows and `python3` elsewhere. Execute them; act on their output; do not
redo by hand what they report.

## 0. Preconditions — stop and tell the developer if one fails

- The working tree is clean.
- The milestone has rules: its scope in the build order, and `### RULE-ID · …` headings in the
  specs for them; no tag is needed, and every rule is planned except `[LATER]` and `[VERIFY]` ones.
  None → stop and say the specs come first. Every rule `[LATER]` or `[VERIFY]` → stop too, and say
  what each waits on.
- `.claude/casefile.json` exists and `.claude/settings.json` has `"worktree": { "baseRef": "head" }`.
  Either missing → propose them as `review` does (step 2), write and commit them after the
  developer's yes. Without the setting, every parallel implementer's worktree branches from the
  remote and misses the specs, the plan and each unpushed commit (D-040). What else `review` step 2 lists — worktrees
  ignored, a linter for an app without one — is proposed the same way when missing (D-042).
- The specs hold together: `write-specs/scripts/spec_lint.py` exits 0. Its errors are shown, and
  the milestone waits until the specs are fixed (`write-specs`); warnings are shown and don't stop it.
- Every tool the milestone's apps need is installed **and running** — a database the integration
  tests use means Docker answering `docker ps`, not just installed: a reviewer that cannot run the
  tests cannot approve.
- **Siblings** (`siblings` in `.claude/casefile.json`): each sibling's folder is readable from this
  session (`permissions.additionalDirectories` in `.claude/settings.json`, proposed as `review` does).

**Siblings.** Every repository holds the same specs, milestone and plan, and builds only the tasks
whose `Repo:` is its own; a task of a sibling is never dispatched from here. This session changes
the status of its own tasks only, and `plan_status.py` reads a sibling task's status from that
sibling's copy of the plan (D-041). Writing into a sibling happens only for its work branch and the
plan, in step 1, and only while it is on that branch with a clean working tree; otherwise stop and
tell the developer. Commit there touching only that file (`git -C <sibling> commit -- <plan>`).

## 1. Branch, mode and plan

- **The branch.** Create the milestone's `feat/` branch, here and in each sibling, following
  [`${CLAUDE_PLUGIN_ROOT}/shared/work-branch.md`](../../shared/work-branch.md). Everything below —
  the plan, every task, every fix record — is committed on it.
- **The mode,** asked with the AskUserQuestion tool:
  - **Task by task** (recommended): one implementer at a time, **without a worktree**, working
    directly on the `feat/` branch, so the developer can follow each change in their own checkout.
  - **Parallel:** every task of a batch at once, each implementer **with a worktree**
    (`isolation: "worktree"` on the dispatch), merged into the `feat/` branch after review. Worth it
    only when a batch holds several parallel-safe tasks.

  Write it under the plan's title as `Mode: task by task` or `Mode: parallel`, so a resumed session
  keeps it.

- No plan file yet, but a sibling has it → copy it here and commit:
  `chore(plans): plan <milestone> from <sibling>`. It was approved there; never re-plan it.
- No plan file anywhere → dispatch `casefile:planner` with the milestone, then read the plan.
- Show the developer the tasks (titles, rules, dependencies), the Blockers and, apart, each planner
  choice `plan_status.py` lists under `choices`, and **wait for their approval**. Each choice is
  accepted or cut on its own: a cut one leaves the task's Notes (D-044). A blocker that is an undecided question is answered by the developer — then the spec is
  amended first, and the task carries the exact rule; never an invented one. Commit the approved plan:
  `chore(plans): plan <milestone>`, here and in each sibling.
- A plan already there is read, never re-planned unless the developer asks.
- **Resume:** for each task `plan_status.py` reports in progress, look for its commit — on the
  `feat/` branch (`git log`) in task-by-task mode, on its worktree branch (`git worktree list`,
  `git log <feat branch>..<branch>`) in parallel mode. A finished commit → tell the developer and
  offer to send it to a reviewer. Nothing there, or the developer says redo → back to `todo`, with
  their yes the worktree branch discarded or the commit reverted (`git revert`).

## 2. Loop until every task is done or blocked

1. **Batch.** Run `implement/scripts/plan_status.py <plan>`. Its `batch` is the next batch; `waiting`
   tasks are held by an open issue or by an entry of the plan's Blockers, and stay out. In
   task-by-task mode, take only the batch's first task.
2. **Implement.** Set each task to `Status: in-progress` in the plan and commit it. Then dispatch
   `casefile:implementer`: `Implement <plan> <task>.`, adding the minor findings carried over from
   earlier tasks that touch the same files.
   - **Task by task:** note `git rev-parse HEAD` as the task's base, and dispatch without a
     worktree. Nobody edits or switches branches in this checkout until it reports.
   - **Parallel:** one implementer per task **in one message**, each with `isolation: "worktree"`.

   Keep each agent's id. A plan change that reaches a running task (after the developer's ruling)
   goes to its implementer as text; never tell an agent to merge, rebase or sync with another branch.
3. **Review.** `STATUS: blocked` → the task becomes `blocked: <reason>`, and the developer hears why.
   `STATUS: done` → dispatch `casefile:reviewer` with the plan path, the task, `BASE:` (the task's base
   commit in task-by-task mode, the `feat/` branch in parallel mode) and the full report. The reviewer
   always works in its own worktree, because it breaks code on purpose.
4. **Fix loop.** `changes-requested` → the blocker and major findings go to **the same implementer**
   (continue it, so it keeps its place): fix, re-run, add a new commit, report again. Two rounds
   without approval → `blocked: review not passing`, findings shown to the developer; in task-by-task
   mode they also decide whether its commits stay or are reverted (`git revert`) before the next task.
5. **Accept** each approved task after the developer's yes.
   - **Task by task:** its commits are already on the `feat/` branch. Set `Status: done (<implementer
     commit>)` in the plan, with unfixed minor findings under "Accepted at merge", and commit:
     `chore(plans): <milestone> <task> done [<rule IDs>]`.
   - **Parallel:** merge it into the `feat/` branch following
     [`${CLAUDE_PLUGIN_ROOT}/shared/merge.md`](../../shared/merge.md).
6. **Conflict at merge** (parallel only). `merge.md` aborts and stops. Tell the developer which files
   conflict. With their yes, dispatch a **new** `casefile:implementer` with a worktree: `Redo <plan>
   <task> from <branch>.` It starts from the current `feat/` branch and writes the work again there.
   Its result is reviewed as a new one, with its own two fix rounds. The old worktree and branch are
   cleaned up with the redo's merge.

**Bugs found along the way** are never fixed inside a task. One in accepted work, reported in an
agent's NOTES or seen in review → propose an issue to the developer and hand it to `fix-bug`, whose
`fix/` branch starts from the `feat/` branch. If it blocks a task, the issue says so (`Blocks: <plan>
<task>`) and `plan_status.py` keeps that task out of every batch until the developer has merged the
fix into the `feat/` branch. A bug in the task under review is a review finding.

## 3. Finish

When `plan_status.py` reports nothing ready and nothing in progress, run
`implement/scripts/rules_coverage.py <plan>` and `fix-bug/scripts/issues_status.py`, and report:
tasks done and blocked (with reasons), issues opened and fixed during the milestone, every rule in
scope as `rules_coverage.py` reports it (covered by a test, untested with its reason, or missing), the
`[MANUAL]` rules as the developer's checklist to test by hand, the sibling tasks still open
(`elsewhere`) and which repository builds them, and what the developer has to decide next, missing
rules and `[VERIFY]` rules waiting on the developer's answer included. End with the `feat/` branch,
ready for the developer to merge into the default branch; never merge it yourself.

## Rules

- Pass **paths and IDs** to agents, never file contents; don't read full diffs yourself — that is the
  reviewer's job. Keep your context small.
- Something unexpected — a report not in its format, a merge conflict, a spec contradiction → stop and
  ask; don't improvise.
- **Never run git or anything else inside an agent's worktree**, nor in this checkout while a
  task-by-task implementer works in it; the one exception is the cleanup in `merge.md` after a merge. An agent's worktree is its own; what needs doing there goes to the agent.
- **A blanket yes covers merges and resuming only** ("merge each one the reviewer approves", "yes to
  all"). A spec gap, a spec-silent choice a reviewer flagged, and any change to an approved plan each
  need the developer's ruling on that point. Record it in the plan quoting them: `Ruled by the
  developer (<date>): "…"`. Never write that the developer approved something they were not asked.
  A flagged choice with no ruling yet stays open and goes in the finish report.
- Never push; never `--force` or `reset --hard` without the developer asking. No co-author or
  "generated by" lines.
