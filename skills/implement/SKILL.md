---
name: implement
description: >
  Use when a milestone of spec rules is to be built: the main session writes its plan, then builds its
  tasks one at a time, test-first, on a feat/ branch, committing each once after the developer says
  yes, until the milestone is done; the developer merges the branch. Resumes a milestone from its plan
  in docs/plans/. Triggers on: "build M2", "implement milestone M3", "build the saved-jobs feature from
  its specs", "continue the milestone", "what's left in M2". Not for one bug (fix-bug), not for
  reviewing one change (review), and not for writing the specs a milestone needs.
---

# Implement a milestone

You plan the milestone and build every task yourself; no agent is dispatched (D-074). The specs define
correct behaviour; the plan file is the record of progress. One task at a time, in the developer's
checkout, and **each task is committed once, after the developer's yes**, with its status in the same
commit (ORCH-003). A review is not part of the loop: the developer asks for `review` when they want one.

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
  tests use means Docker answering `docker ps`, not just installed: a task whose tests cannot run
  cannot be accepted.
- **Siblings** (`siblings` in `.claude/casefile.json`): each sibling's folder is readable from this
  session (`permissions.additionalDirectories` in `.claude/settings.json`, proposed as `review` does).

**Siblings.** Every repository holds the same specs, milestone and plan, and builds only the tasks
whose `Repo:` is its own; a task of a sibling is never built from here. This session changes the
status of its own tasks only, and `plan_status.py` reads a sibling task's status from that sibling's
copy of the plan (D-041). Writing into a sibling happens only for its work branch and the plan, in
step 1, and only while it is on that branch with a clean working tree; otherwise stop and tell the
developer. Commit there touching only that file (`git -C <sibling> commit -- <plan>`).

## 1. Branch and plan

- **The branch.** Create the milestone's `feat/` branch, here and in each sibling, following
  [`${CLAUDE_PLUGIN_ROOT}/shared/work-branch.md`](../../shared/work-branch.md). Everything below is
  committed on it.
- No plan file yet, but a sibling has it → copy it here and commit:
  `chore(plans): plan <milestone> from <sibling>`. It was approved there; never re-plan it.
- No plan file anywhere → write it yourself, following
  [`references/planning.md`](references/planning.md) (ORCH-015).
- Show the developer the tasks (titles, rules, dependencies), the Blockers and, apart, each planner
  choice `plan_status.py` lists under `choices`, and **wait for their approval**. Each choice is
  accepted or cut on its own: a cut one leaves the task's Notes (D-044). A blocker that is an undecided
  question is answered by the developer — then the spec is amended first, and the task carries the
  exact rule; never an invented one. Commit the approved plan: `chore(plans): plan <milestone>`, here
  and in each sibling.
- A plan already there is read, never re-planned unless the developer asks.
- **Resume.** Uncommitted work in the checkout is the next task's, left by an earlier session: tell the
  developer, and continue it, or with their yes discard it (`git reset --hard HEAD`, then remove the
  untracked files they confirm).

## 2. Loop until every task is done or blocked

1. **Next task.** Run `implement/scripts/plan_status.py <plan>`. Its `batch` is the one next task;
   `waiting` tasks are held by an open issue or by an entry of the plan's Blockers, and stay out.
2. **Build it** following [`${CLAUDE_PLUGIN_ROOT}/shared/build-task.md`](../../shared/build-task.md)
   (ORCH-016), and report to the developer as it says.
3. **Blocked** (ORCH-012). Tell the developer why. Set `Status: blocked: <reason>` and commit the plan
   alone: `git commit -m "chore(plans): <milestone> <task> blocked" -- <plan>`. The task's work stays
   uncommitted in the checkout, listed to the developer, who keeps, stashes or drops it before the next
   task: the pre-commit gate would otherwise test it with the next commit.
4. **Accept** (ORCH-003), after the developer's yes for this task. Set `Status: done` in the plan. If
   the change touched an app that has an `image` command, run it first: a green suite has passed with a
   broken image before. Then `git add -A`, and commit **once**:
   `<type>(<scope>): <what> [<rule IDs>]` — the type fits the change (`feat`, `fix`, `test`,
   `refactor`, `docs`…), e.g. `feat(jobs): score required skills at 70% [MATCH-010]`. The pre-commit
   gate runs the tests. That is the task's only commit.

**A bug found along the way** in accepted work → propose an issue to the developer and hand it to
`fix-bug`, whose `fix/` branch starts from the `feat/` branch. If it blocks
a task, the issue says so (`Blocks: <plan> <task>`) and `plan_status.py` keeps that task out of every
batch until the developer has merged the fix into the `feat/` branch.

## 3. Finish

When `plan_status.py` reports nothing ready and nothing in progress, run
`implement/scripts/rules_coverage.py <plan>` and `fix-bug/scripts/issues_status.py`, and report:
tasks done and blocked (with reasons), issues opened and fixed during the milestone, every rule in
scope as `rules_coverage.py` reports it (covered by a test, untested with its reason, or missing), the
`[MANUAL]` rules as the developer's checklist to test by hand, the sibling tasks still open
(`elsewhere`) and which repository builds them, and what the developer has to decide next, missing
rules and `[VERIFY]` rules waiting on the developer's answer included. End with the `feat/` branch,
ready for the developer to review (`review`) if they want, and to merge into the default branch; never
merge it yourself.

## Rules

- **A blanket yes covers accepting and resuming only** ("commit each task", "build and execute"). A
  spec gap, a spec-silent choice, and any change to an approved plan each need the developer's ruling
  on that point. Record it in the plan quoting them: `Ruled by the developer (<date>): "…"`. Never write
  that the developer approved something they were not asked. A choice with no ruling yet stays open
  and goes in the finish report.
- Never push; never `--force` or `reset --hard` without the developer asking. No co-author or
  "generated by" lines.
