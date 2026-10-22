---
name: implement
description: >
  Use when a milestone of spec rules is to be built: its plan written by devflow:planner, then its
  tasks run in parallel worktrees by devflow:implementer, each reviewed by devflow:reviewer and merged
  after the developer says yes, until the milestone is done. Resumes a milestone from its plan in
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

- The working tree is clean and the current branch is the default branch (`.claude/devflow.json`,
  else `main`).
- The milestone has rules: its scope in the build order, and `### RULE-ID · …` headings in the
  specs for them; no tag is needed, and every rule is planned except `[LATER]` and `[VERIFY]` ones.
  None → stop and say the specs come first. Every rule `[LATER]` or `[VERIFY]` → stop too, and say
  what each waits on.
- `.claude/devflow.json` exists and `.claude/settings.json` has `"worktree": { "baseRef": "head" }`.
  Either missing → propose them as `review` does (step 2), write and commit them after the
  developer's yes. Without the setting, every agent branches from the remote and misses the specs,
  the plan and each unpushed merge (D-040). What else `review` step 2 lists — worktrees
  ignored, a linter for an app without one — is proposed the same way when missing (D-042).
- The specs hold together: `write-specs/scripts/spec_lint.py` exits 0. Its errors are shown, and
  the milestone waits until the specs are fixed (`write-specs`); warnings are shown and don't stop it.
- Every tool the milestone's apps need is installed **and running** — a database the integration
  tests use means Docker answering `docker ps`, not just installed: a reviewer that cannot run the
  tests cannot approve.
- **Siblings** (`siblings` in `.claude/devflow.json`): each sibling's folder is readable from this
  session (`permissions.additionalDirectories` in `.claude/settings.json`, proposed as `review` does).

**Siblings.** Every repository holds the same specs, milestone and plan, and builds only the tasks
whose `Repo:` is its own; a task of a sibling is never dispatched from here. This session changes
the status of its own tasks only, and `plan_status.py` reads a sibling task's status from that
sibling's copy of the plan (D-041). Writing into a sibling happens only for the plan, in step 1, and
only while it is on its default branch with a clean working tree; otherwise stop and tell the
developer. Commit there touching only that file (`git -C <sibling> commit -- <plan>`).

## 1. Plan

- No plan file yet, but a sibling has it → copy it here and commit:
  `chore(plans): plan <milestone> from <sibling>`. It was approved there; never re-plan it.
- No plan file anywhere → dispatch `devflow:planner` with the milestone, then read the plan.
- Show the developer the tasks (titles, rules, dependencies), the Blockers and, apart, each planner
  choice `plan_status.py` lists under `choices`, and **wait for their approval**. Each choice is
  accepted or cut on its own: a cut one leaves the task's Notes (D-044). A blocker that is an undecided question is answered by the developer — then the spec is
  amended first, and the task carries the exact rule; never an invented one. Commit the approved plan:
  `chore(plans): plan <milestone>`, here and in each sibling.
- A plan already there is read, never re-planned unless the developer asks.
- **Resume:** for each task `plan_status.py` reports in progress, look at its worktree branch
  (`git worktree list`, `git log <default>..<branch>`). A finished commit there → tell the developer
  and offer to send it to a reviewer. Nothing there, or the developer says redo → back to `todo`, the
  branch discarded with their yes.

## 2. Loop until every task is done or blocked

1. **Batch.** Run `implement/scripts/plan_status.py <plan>`. Its `batch` is the next batch; `waiting`
   tasks are held by an open issue or by an entry of the plan's Blockers, and stay out.
2. **Implement.** Set each batch task to `Status: in-progress` in the plan, then dispatch one
   `devflow:implementer` per task **in one message**: `Implement <plan> <task>.` Add the minor
   findings carried over from earlier tasks that touch the same files. Keep each agent's id. A plan
   change that reaches a running task (after the developer's ruling) goes to its implementer as text;
   never tell an agent to merge, rebase or sync with the default branch.
3. **Evals and review.** `STATUS: blocked` → the task becomes `blocked: <reason>`, and the developer
   hears why. After an implementer's commit, follow
   [`${CLAUDE_PLUGIN_ROOT}/shared/task-evals.md`](../../shared/task-evals.md), then dispatch
   `devflow:reviewer` with the plan path, task, full report and main-session eval results.
4. **Fix loop.** `changes-requested` → the blocker and major findings go to **the same implementer**
   (continue it, so it keeps its worktree): fix, re-run, add a new commit, report again. The main
   session then repeats the task eval step for the new commit before another review. Two rounds
   without approval → `blocked: review not passing`, findings shown to the developer.
5. **Merge** each approved task after the developer's yes, following
   [`${CLAUDE_PLUGIN_ROOT}/shared/merge.md`](../../shared/merge.md).
6. **Conflict at merge.** `merge.md` aborts and stops. Tell the developer which files conflict. With
   their yes, dispatch a **new** `devflow:implementer`: `Redo <plan> <task> from <branch>.` It starts
   from the current default branch and writes the work again there. Its result is reviewed as a new
   one, with its own two fix rounds. The old worktree and branch are cleaned up with the redo's merge.

**Bugs found along the way** are never fixed inside a task's branch. One in merged work, reported in
an agent's NOTES or seen in review → propose an issue to the developer and hand it to `fix-bug`. If it
blocks a task, the issue says so (`Blocks: <plan> <task>`) and `plan_status.py` keeps that task out of
every batch until the issue is fixed. A bug inside a task's own unmerged branch is a review finding.

## 3. Finish

When `plan_status.py` reports nothing ready and nothing in progress, run
`implement/scripts/rules_coverage.py <plan>` and `fix-bug/scripts/issues_status.py`, and report:
tasks done and blocked (with reasons), issues opened and fixed during the milestone, every rule in
scope as `rules_coverage.py` reports it (covered by a test or rule-named eval, untested with its reason,
or missing), each task eval's actual result (an eval's existence is not a passing run), all unrun
shell-enabled cases with the command for the developer to run on Fedora, the
`[MANUAL]` rules as the developer's checklist to test by hand (the milestone is done only after the
developer's ok on each), the sibling tasks still open
(`elsewhere`) and which repository builds them, and what the developer has to decide next, missing
rules and `[VERIFY]` rules waiting on the developer's answer included.

## Rules

- Pass **paths and IDs** to agents, never file contents; don't read full diffs yourself — that is the
  reviewer's job. Keep your context small.
- Something unexpected — a report not in its format, a merge conflict, a spec contradiction → stop and
  ask; don't improvise.
- **Never run git or anything else inside an agent's worktree** except the main-session task-eval
  commands in step 2.3 and cleanup in `merge.md` after a merge. Other work there goes to the agent.
- **A blanket yes covers merges and resuming only** ("merge each one the reviewer approves", "yes to
  all"). A spec gap, a spec-silent choice a reviewer flagged, and any change to an approved plan each
  need the developer's ruling on that point. Record it in the plan quoting them: `Ruled by the
  developer (<date>): "…"`. Never write that the developer approved something they were not asked.
  A flagged choice with no ruling yet stays open and goes in the finish report.
- Never push; never `--force` or `reset --hard` without the developer asking. No co-author or
  "generated by" lines.
