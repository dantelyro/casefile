# 0.20.0 — the reviewer runs the breaks — implementation plan

**Spec:** `docs/specs/2026-10-19-reviewer-breaks-and-existing-code-specs-design.md`, section 0.20.0
(approved 2026-10-19).
**Starts from:** `a0dd8a3` on `main`, version `0.19.1` (unpushed).
**Ships as:** `0.20.0`.

**Goal:** the agent that writes a test never proves it can fail. The implementer writes tests and
code; the reviewer breaks the code under each rule's main test in its own worktree, quotes each
result, restores it, and still never commits (D-045).

**How this plan is run:** as 0.16.0's: task by task, test first, each committed when green. Task 6,
the live test, needs the developer.

## Global constraints

Standard library only, Python ≥ 3.10, `unittest`, each rule tested both ways and mutation-checked,
conventional commits, each rule stated once. Hooks keep failing closed (D-028).

## Files

| Path | Task | What |
|---|---|---|
| `hooks/devflow_hooks/lib.py` | 1 | Whether a path lies inside a linked worktree |
| `hooks/devflow_hooks/guard_paths.py`, `tests/test_guard_paths.py` | 1 | The reviewer edits only inside a linked worktree, never tests or records |
| `hooks/devflow_hooks/guard_bash.py`, `tests/test_guard_bash.py` | 2 | The reviewer may `git restore <paths>` |
| `agents/reviewer.md` | 3 | Runs the breaks, BREAKS line, description |
| `agents/implementer.md` | 4 | Step 5 and BREAKS removed; `RED: none` for behaviour that already exists |
| `docs/specs/2026-10-14-review-design.md`, README, `CLAUDE.md`, manifests, D-045 | 5 | Docs and version |

## Task 1 — `guard_paths`: the reviewer edits only inside a linked worktree

- [ ] Tests first, in a temporary repository with a linked worktree (`git worktree add`), as
      `test_inside_a_real_worktree` builds one:
  - `devflow:reviewer` writing a product file inside the linked worktree → allow.
  - The same file in the main checkout → deny, the reason saying breaks happen only in the
    reviewer's own worktree.
  - A test file inside the linked worktree (`TEST_FILE` from `pre_commit.py`: `tests/x.py`,
    `web/a.test.ts`, `e2e/login.spec.ts`) → deny.
  - Inside the linked worktree: `.claude/…`, `docs/issues/…`, the plans and specs folders, a
    `protected_paths` entry → deny.
  - A path outside any repository → deny.
  - `NotebookEdit` follows the same rules.
  - `test_writes_nothing` is replaced by the cases above; the planner and implementer cases are
    unchanged.
- [ ] `lib.in_linked_worktree(path)`: the git root of the path's folder, and `rev-parse --git-dir`
      differs from `--git-common-dir`. Fails closed: any git error is "not linked".
- [ ] `guard_paths`: the reviewer branch uses it; `TEST_FILE` is imported from `pre_commit`, not
      copied.

## Task 2 — `guard_bash`: `git restore` for the reviewer

- [ ] Tests first:
  - `devflow:reviewer`: `git restore web/x.ts` and `git restore -- web/x.ts web/y.ts` → allow.
  - `git restore --staged …`, `-S`, `--source=…`, `-s …`, and `git restore` with no path → deny.
  - Still denied: `git add`, `commit`, `stash`, `checkout -- <file>`, `reset`, `sed -i`, redirects.
  - `devflow:planner`: `git restore web/x.ts` → deny (split out of `test_changes_nothing`).
- [ ] `_read_only_violation` takes the role; only the reviewer gets the `restore` exception.

## Task 3 — The reviewer runs the breaks

- [ ] `agents/reviewer.md`:
  - Process: a new step after the re-run. Check `git status --porcelain` is empty first. For each
    rule's main test, break the line behind the rule, run that test, quote the failure, restore with
    `git restore <file>`. Then its own breaks along the test's code path (wrong branch, missing
    filter, redundant check, off by one) and the edge cases the rule names or implies, the same way.
    End with `git status --porcelain` empty.
  - Checklist: "Tests can fail" rewritten around the executed breaks. A break that stays green is
    major, for any rule. A break that fails on a crash or an import error is not red. An edge case
    the code gets wrong is a finding with the input that shows it. "Red was real" gains the
    `RED: none` case: accepted only when the diff touches no product code.
  - Output block gains `BREAKS: <per test: the change → red (the failing assertion) | green>; git
    status: clean`. A worktree not clean at the end → no verdict, say why.
  - Rules: "Never edit, create or delete files" becomes: edit only to break product code in your own
    worktree, restore every break, never write a test for what you find, never commit.
  - Inputs: BREAKS leaves the list of implementer report fields.
  - `description`: "Never edits code" → "never commits; edits only to break code in its own worktree,
    and restores it".
- [ ] One command per call still holds (D-043): each break's test run is its own call, with a
      timeout.

## Task 4 — The implementer stops proving its own tests

- [ ] `agents/implementer.md`: step 5 (break check) removed and the steps renumbered; `BREAKS:` leaves
      the output block.
- [ ] Step 2 gains: when the task's behaviour already exists, the tests pass on the first run; report
      `RED: none — <test> passed on first run`, and touch no product code.
- [ ] Grep the repo for every other `BREAKS` and break-check mention (skills, `shared/merge.md`,
      README) and update it.

## Task 5 — Docs, decision, version

- [ ] `2026-10-14-review-design.md`: the `reviewer` rows (Summary table, guard table) point to the
      0.20.0 spec for its file and `git restore` rules.
- [ ] README: the reviewer's and implementer's descriptions. `CLAUDE.md`: any sentence the change
      makes false; watermark moved in the same commit.
- [ ] D-045: `Implemented by` with the commits of tasks 1–4.
- [ ] `plugin.json` version `0.20.0`. `python -m unittest discover -s tests` green.

## Task 6 — Live test (needs the developer)

The spec's test: on a real project, a reviewer runs the breaks itself and catches a test that is too
weak, and leaves nothing behind.

- [ ] On a throwaway clone of a pilot project, with the developer's yes: one task or issue through
      `implement` or `fix-bug`, where the developer weakens one test before the review (an assertion
      that would pass with the rule's line broken).
- [ ] Expected: the report's BREAKS shows that break green, as a major finding; every other break red
      on an assertion; `git status: clean`; the reviewer made no commit, and nothing changed in the
      main checkout.
- [ ] Record what broke here, and fix it before shipping.
