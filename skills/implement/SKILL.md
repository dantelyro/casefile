---
name: implement
description: >
  Use when a milestone of spec rules is to be built: its plan written by casefile:planner, then its
  tasks built one at a time on a feat/ branch by casefile:implementer, each reviewed by
  casefile:reviewer and committed once after the developer says yes, until the milestone is done;
  the developer merges the branch. Resumes a milestone from its plan in
  docs/plans/. Triggers on: "build M2", "implement milestone M3", "build the saved-jobs feature from
  its specs", "continue the milestone", "what's left in M2". Not for one bug (fix-bug), not for
  reviewing one change (review), and not for writing the specs a milestone needs.
---

# Implement a milestone

You are the **orchestrator**. You coordinate agents and keep the plan; you never write product code,
tests or specs yourself. The specs define correct behaviour; the plan file is the single record of
progress. **You are the only one who commits**: each task once, after review, with its status in the
same commit. One task at a time, in the developer's checkout, with no worktrees (D-072).

Scripts below run as `<python> "${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<name>.py"`, where
`<python>` is `py -3` on Windows and `python3` elsewhere. Execute them; act on their output; do not
redo by hand what they report.

## 0. Preconditions — stop and tell the developer if one fails

- The working tree is clean.
- The milestone has rules: its scope in the build order, and `### RULE-ID · …` headings in the
  specs for them; no tag is needed, and every rule is planned except `[LATER]` and `[VERIFY]` ones.
  None → stop and say the specs come first. Every rule `[LATER]` or `[VERIFY]` → stop too, and say
  what each waits on.
- `.claude/casefile.json` exists. Missing → propose it as `review` does (step 2), write and commit it
  after the developer's yes. What else `review` step 2 lists — a linter for an app without one — is
  proposed the same way when missing (D-042).
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

## 1. Branch and plan

- **The branch.** Create the milestone's `feat/` branch, here and in each sibling, following
  [`${CLAUDE_PLUGIN_ROOT}/shared/work-branch.md`](../../shared/work-branch.md). Everything below —
  the plan, every task, every fix record — is committed on it.
- No plan file yet, but a sibling has it → copy it here and commit:
  `chore(plans): plan <milestone> from <sibling>`. It was approved there; never re-plan it.
- No plan file anywhere → dispatch `casefile:planner` with the milestone, then read the plan.
- Show the developer the tasks (titles, rules, dependencies), the Blockers and, apart, each planner
  choice `plan_status.py` lists under `choices`, and **wait for their approval**. Each choice is
  accepted or cut on its own: a cut one leaves the task's Notes (D-044). A blocker that is an undecided question is answered by the developer — then the spec is
  amended first, and the task carries the exact rule; never an invented one. Commit the approved plan:
  `chore(plans): plan <milestone>`, here and in each sibling.
- A plan already there is read, never re-planned unless the developer asks.
- **Resume** (ORCH-008): a task `plan_status.py` reports in progress has its work saved under
  `refs/casefile/wip/<milestone>/<task>`. Work still staged in the checkout → tell the developer and
  offer to send it to a reviewer. Not there → restore it first:
  `git restore --source=<ref> --staged --worktree .`. The developer says abandon → with their yes,
  `git reset --hard HEAD` and `git update-ref -d <ref>`; the task is `todo` again.

## 2. Loop until every task is done or blocked

`<ref>` below is `refs/casefile/wip/<milestone>/<task>`, the milestone being the plan's file name.
Nobody edits or switches branches in this checkout while an agent works in it.

1. **Next task.** Run `implement/scripts/plan_status.py <plan>`. Its `batch` is the one next task;
   `waiting` tasks are held by an open issue or by an entry of the plan's Blockers, and stay out.
2. **Implement.** Commit nothing. Dispatch `casefile:implementer` without a worktree:
   `Implement <plan> <task>.`, adding the minor findings carried over from earlier tasks that touch
   the same files. Keep its id. A plan change that reaches the running task (after the developer's
   ruling) goes to it as text.
3. **Save, then review** (ORCH-004). `STATUS: blocked` → step 6. `STATUS: done` → stage and save the
   work, one command each:
   - `git add -A`
   - `git write-tree`, then `git commit-tree <tree> -p HEAD -m "wip <milestone> <task>"`, then
     `git update-ref <ref> <commit>`

   Then dispatch `casefile:reviewer` without a worktree, with the plan path, the task and the full
   report. It reviews the staged change in this checkout.
4. **Check the checkout** (ORCH-005), before reading the verdict: `git diff --quiet` and
   `git ls-files --others --exclude-standard` printing nothing mean the working files match the staged
   copy. Otherwise `git restore .`, and tell the developer about every untracked file it left.
5. **Fix loop.** `changes-requested` → the blocker and major findings go to **the same implementer**
   (continue it, so it keeps its place): it fixes on top of its uncommitted work and reports again;
   save and review again from step 3. Two rounds without approval → step 6, with
   `blocked: review not passing` and the findings shown to the developer.
6. **Blocked** (ORCH-012). Save the work as in step 3 so it is kept, and tell the developer why. With
   their yes, clear the checkout (`git reset --hard HEAD`): the work stays under `<ref>`, and the
   pre-commit gate would otherwise test it with the next commit. Then set `Status: blocked: <reason>`
   and commit the plan alone: `chore(plans): <milestone> <task> blocked`.
7. **Accept** (ORCH-003), after the developer's yes for this task. Set `Status: done` in the plan, with
   unfixed minor findings under "Accepted". If the change touched an app that has an `image` command,
   run it first: a green suite has passed with a broken image before. Then `git add -A`, and commit
   **once**:
   `<type>(<scope>): <what> [<rule IDs>]` — the type fits the change (`feat`, `fix`, `test`,
   `refactor`, `docs`…), e.g. `feat(jobs): score required skills at 70% [MATCH-010]`. The pre-commit
   gate runs the tests. Then `git update-ref -d <ref>`. That is the task's only commit.

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
- Something unexpected — a report not in its format, a spec contradiction → stop and ask; don't
  improvise.
- **Never run git or edit anything in this checkout while an agent works in it.**
- **A blanket yes covers accepting and resuming only** ("commit each one the reviewer approves", "yes
  to all"). A spec gap, a spec-silent choice a reviewer flagged, and any change to an approved plan each
  need the developer's ruling on that point. Record it in the plan quoting them: `Ruled by the
  developer (<date>): "…"`. Never write that the developer approved something they were not asked.
  A flagged choice with no ruling yet stays open and goes in the finish report.
- Never push; never `--force` or `reset --hard` without the developer asking. No co-author or
  "generated by" lines.
