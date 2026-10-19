# The reviewer runs the breaks, and specs for existing code — design

**Date:** 2026-10-19.
**Status:** Approved 2026-10-19. Not yet implemented.
**Release:** `0.20.0` (the reviewer runs the breaks), then `0.21.0` (`write-specs` specs existing
code). `0.21.0` needs `0.20.0`: a milestone of tests for existing code has no red, so its only proof
that the tests can fail is the reviewer's breaks.

## Summary

| Piece | Release | What changes |
|---|---|---|
| `devflow:implementer` | 0.20.0 | Loses its break check (step 5) and the BREAKS line. Writes tests and code; never proves its own tests can fail. |
| `devflow:reviewer` | 0.20.0 | Runs the breaks itself, in its own worktree, then restores them. Still never commits. |
| `guard_paths`, `guard_bash` | 0.20.0 | The reviewer may edit inside its own linked worktree, and run `git restore`. |
| `write-specs` | 0.21.0 | Also drafts rules from code that already exists; the milestone it adds holds tests-only tasks. |

No new skill and no new agent. Tests for an existing codebase go through the same path as any feature:
`write-specs` → `implement` (D-046).

## Why

Every proof that a test can fail was run by the agent that wrote the test.

- **0.15.0 live run** (`docs/plans/2026-10-16-implement.md`): 2 of 10 breaks made by hand survived the
  suites, and two of three reviewers only reasoned about breaks instead of finding them.
- **PetTool, devflow 0.16.1** (two repositories, M0): the milestone only added tests for existing
  screens, so every test passed first time and each report justified `RED: n/a`. The breaks were the
  only proof. The reviewer's hooks block every edit, so it could only reason about them; when an
  implementer was stopped without a report, nobody had run the second round's breaks, and the main
  session ran them during the merge.

## 0.20.0 — the reviewer runs the breaks

### R1. The implementer

- Step 5 (break check) and the `BREAKS:` line of the report are removed.
- RED is unchanged, with one case added: when a task's behaviour already exists, its tests pass on the
  first run. The report says `RED: none — <test> passed on first run`. The reviewer accepts that only
  when the diff touches no product code; otherwise it is a major finding, as a missing RED is today.

### R2. The reviewer

After the re-run (process step 3), on a clean worktree:

1. For each rule's main test: break the line that implements the rule, run that test, quote the
   failure, and restore the file with `git restore <file>`.
2. Then its own breaks along the code path the test covers — a wrong branch, a missing filter, a
   redundant check, a constant off by one — and the edge cases the rule names or implies. Same run,
   quote, restore.
3. End with `git status --porcelain` empty, quoted in the report.

The report gains a line:

```
BREAKS: <per test: the change → red (the failing assertion) | green>; git status: clean
```

- A break that stays green is a **major** finding, for any rule. Name the test and the change.
- A break that fails on a crash or an import error instead of an assertion does not count as red.
- An edge case the code gets wrong is a finding against the code, with the input that shows it.
- A worktree not clean at the end is a blocker against the review itself: the verdict is not given.
- The checklist's "Tests can fail" item is rewritten around executed breaks; "Red was real" gains
  R1's case.

The reviewer still never fixes what it finds, never writes a test for an edge case it found, and
never commits (D-045).

### R3. `guard_paths`

| Agent | May edit |
|---|---|
| `reviewer` | Only files inside a **linked** worktree (its git dir differs from its common dir), never the main checkout; never test files (`TEST_FILE` in `pre_commit.py`), a `.claude` folder, `docs/issues/`, the plans or specs folders, or `protected_paths`. |

Reasons go in the deny message, as for the other agents: the reviewer breaks product code, it does
not change tests or records.

### R4. `guard_bash`

The reviewer's read-only rules stay, with one exception: `git restore <paths>`, without `--staged`,
`-S` or `--source`. `git add`, `commit`, `stash`, `checkout`, `reset` and file-changing shell stay
denied.

### R5. Specs, descriptions and tests

- The `reviewer` row of the guard table in `2026-10-14-review-design.md` points to this spec.
- `agents/reviewer.md` description: "Never edits code" becomes "never commits; edits only to break code
  in its own worktree and restores it".
- `tests/test_guard_paths.py` and `tests/test_guard_bash.py` cover R3 and R4: allowed in a linked
  worktree, denied in the main checkout, denied for a test file, `git restore` allowed, `--staged` and
  `--source` denied.

## 0.21.0 — `write-specs` specs existing code

### S1. Rules drafted from existing code

`write-specs` takes a new kind of input: code that already exists ("spec the existing login flow",
"write specs for what checkout does today").

- It reads the code in the named scope and drafts one rule per behaviour it observes, in the usual
  format and area files, each with a new ID.
- **Every such rule is shown as proposed.** Code shows what a system does, never what it must do
  (the evidence skill's Grade 4); the rule becomes a requirement only at the developer's yes.
- The milestone it adds holds tests-only tasks. The planner marks them so in each task; the
  implementer reports R1's `RED: none`, and the reviewer's breaks are the proof.

### S2. Behaviour that looks wrong

Never drafted as a rule. It goes to the approval step as a question ("`formatPrice(-500)` returns
`R$ -5,00`: should it be an error?"). The answer becomes a rule, or an issue for `fix-bug` after the
developer's yes. A test is never written to assert behaviour that looks like a bug.

### S3. Trigger surface

The `description` gains this case and its trigger phrases. That changes when the skill fires, so the
release adds eval cases: at least two that should trigger (existing code to spec) and one that should
not (a request to fix a bug in it).

## Decisions to record when implemented

- **D-045** — The reviewer runs the breaks, in its own worktree; the implementer no longer proves its
  own tests. (Recorded with this spec.)
- **D-046** — Tests for existing code are specified by `write-specs` and built by `implement`; there is
  no separate test-writing skill. (Recorded with this spec.)

## Not in this release

- **The reviewer working in the implementer's worktree** (one worktree per change, not per agent
  run; PetTool #7). Needs a live probe first: whether an agent without `isolation` keeps its shell in
  another folder after `cd`, and whether the `cwd` the hooks see follows it. Undocumented; the hooks
  depend on both.
- **A Kind field for tasks** (`Kind: characterization`). R1's `RED: none` case and the planner's
  tests-only note cover it without a new field.
