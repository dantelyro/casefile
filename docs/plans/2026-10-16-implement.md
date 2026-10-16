# 0.15.0 — `implement`, the planner and the plan scripts — implementation plan

**Spec:** `docs/specs/2026-10-14-implement-design.md` (approved 2026-10-14).
**Starts from:** `22a26c7` on `main`, version `0.14.1`.
**Ships as:** `0.15.0`.

**Goal:** Inverso's `build-milestone` as a devflow skill. `devflow:planner` turns one milestone of
rules into small test-first tasks; `implement` runs them in parallel worktrees through the
implementer, the reviewer and the shared merge, with the mechanical steps — which tasks are ready,
which rules have tests — done by scripts.

**How this plan is run:** as 0.14.0's: task by task, test first, each committed when green (the
developer's standing instruction, 2026-10-15). Task 6, the live test, needs the developer: their own
session is building Inverso's M2 with `build-milestone`, the milestone the spec names for this test.

## Global constraints

As 0.13.0 and 0.14.0: standard library only, Python ≥ 3.10, `unittest`, each rule tested both ways
and mutation-checked, conventional commits, each rule stated once, nothing written into a project
that has not agreed to it.

## Files

| Path | Task | What |
|---|---|---|
| `skills/implement/scripts/plan_status.py` | 1 | Ready tasks, the next batch, stuck and waiting tasks |
| `skills/implement/scripts/rules_coverage.py` | 2 | Rules in scope with and without a test named after them |
| `agents/planner.md` | 3 | `devflow:planner` |
| `skills/implement/SKILL.md` | 4 | The orchestrator |
| `evals/implement-*`, `evals/not-implement-*` | 4 | Trigger evals |
| `docs/decisions/0034…0035`, docs, manifests | 5 | Decisions, docs, version |

## Task 1 — `plan_status.py <plan>`

- [ ] Tests first, on plan files in Inverso's format (`### T3 · Title`, `- Status:`, `- Depends on:`,
      `- Parallel-safe with:`, …) in a temporary repository:
  - statuses parsed: `todo`, `in-progress`, `done (<commit>)`, `blocked: <reason>`; anything else is
    an error naming the task;
  - **ready** = `todo`, every dependency `done`, and no open issue in `docs/issues/` whose `Blocks:`
    names this plan and task (read through `issues_status.py --blocks`, never re-parsed here);
  - **batch** = the first ready task plus the ready tasks it lists as parallel-safe *and* that list it
    back, at most 3 (`--max` to change);
  - **in progress** listed separately (the resume rule needs them), **waiting** = todo tasks held by an
    open issue, with the issue ids;
  - a dependency on a task that does not exist is an error;
  - `--json` and plain text; exit 1 on errors.

## Task 2 — `rules_coverage.py <plan>`

- [ ] Tests first:
  - the rules in scope are the plan's `Rules covered` section, each looked up in the specs folder
    (`specs_dir`) for its tag; a rule ID missing from the specs is an error;
  - a rule **has a test** when a test file contains a test named after it: `RULE-010:` or `RULE-010 `
    in a quoted name (Jest, Vitest, Playwright) or `test_RULE_010` (pytest, unittest);
  - `[MANUAL]` rules are listed as checked in review, never as missing; `[LATER]` are out of scope;
  - exit 1 when an `[MVP]` rule in scope has no test;
  - `rule_id_pattern` from config.
- Deviation, as in 0.14.0: "passed in the last run" becomes "has a test"; passing is shown at merge,
  where every touched app's suite runs.

## Task 3 — The planner agent

- [ ] `agents/planner.md` from Inverso's, generalised: inputs are a scope (a milestone in the build
      order); the build order's location and the specs folder from config (`build_order`, default
      `docs/product/blueprint.html`; `specs_dir`); the plan format above; `EXISTS` when the plan is
      already there; `[VERIFY]` and spec gaps go under Blockers, never planned around; every task names
      its rules and its failing test; a task touching more than ~5 files is split; a data rule's test
      names its second user. `model: opus`. It writes only its plan file (the file guard enforces it).
- [ ] `build_order` added to the config defaults.
- [ ] Live check: `devflow:planner` loads; a write outside its plan file is refused.

## Task 4 — The `implement` skill

- [ ] `skills/implement/SKILL.md`, from Inverso's `build-milestone` with its lessons: preconditions
      (clean tree on the default branch, tools installed *and running*); plan (the planner, the
      developer's approval of tasks and blockers, `chore(plans): plan <scope>`); the resume rule (an
      `in-progress` task's branch is checked for a finished commit, offered for review, never
      discarded unasked); the loop driven by `plan_status.py` (batch → implementers in one message →
      a reviewer per result → fix loop ≤ 2 rounds through the same implementer → the shared merge
      after the developer's yes); bugs found along the way become issues through `fix-bug`; spec gaps
      are asked, never invented; carry-over minors go into the next task's prompt; the finish report
      with `rules_coverage.py`. Never writes product code, tests or specs itself.
- [ ] Trigger evals with small fixture repositories: fires for "build M2", "implement the saved-jobs
      milestone", "continue the milestone"; does not fire for "fix this bug" (fix-bug) or "review T3"
      (review).

## Task 5 — Decisions, docs, version

- [ ] D-034 rules with IDs are the unit of specification, testing and review; D-035 the orchestrator
      never writes product code, tests or specs, and the plan file is the progress record.
- [ ] README, CLAUDE.md, manifests, version `0.15.0`.

## Task 6 — Live test on Inverso (needs the developer)

The spec's test is building Inverso's M2 with `implement` instead of `build-milestone`. The developer's
own session is already building M2 with `build-milestone`; how to test 0.15.0 is theirs to decide.
