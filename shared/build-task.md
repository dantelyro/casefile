# Building a task

Used by `implement` and `fix-bug`. You build one plan task or one bug fix yourself, test-first, in the
developer's checkout, and leave it uncommitted until the developer says yes (ORCH-016, ORCH-017).

## Before writing anything

- **Read** the task — its rules, test names, files, "Done when" check, `Reuse:` line and every Notes
  item, which are part of the task — or the issue: what happens, what should happen, how to see it, the
  test that must fail first. Then every spec rule named, the project's `CLAUDE.md`, and the code around
  the files you will touch. Anything on screen: the design system first; if it lacks something, stop and
  tell the developer instead of inventing a style.
- **Check the decisions**: the index and, in full, every decision touching the task's rules or files.
  A task or fix that would contradict one, or bring back something dropped, reverted or superseded, is
  not built: stop, and it becomes blocked naming the decision (D-065).
- **Set up**: dependencies missing or behind the lock file → the app's `install` command from
  `.claude/casefile.json`.

## Red, green, refactor

1. **Red.** Write the tests first, each named after its rule ID (`MATCH-010: …`, `test_MATCH_010_…`);
   for an issue, the test under "Test that must fail first". Add stubs with the real names and
   signatures so every test reaches its assertions. Run them in a step of its own and read the output
   before writing any implementation: each rule test must **fail on an assertion**. A missing module or
   name, a typo or an import error is not red yet; fix the stub and run again. A test about one user's
   data has a second user whose data overlaps.
   - The behaviour already exists and the tests pass on the first run → `RED: none — <test> passed on
     first run`, and no product code is touched.
   - **For an issue, the test reproduces the reported behaviour through the code the bug is in**, as
     "How to see it" describes, so undoing the fix turns it red again. A test of a helper you are about
     to write fails only because the helper is missing, and stays green if the bug comes back.
2. **Green.** The least code that makes them pass.
3. **Refactor.** Clean names and duplication without changing behaviour; run the tests again.
4. **Check.** The task's "Done when", then the `test` and `lint` commands of every app you touched.

## Rules

- **Only this task.** A bug elsewhere is proposed to the developer as an issue for `fix-bug`; never
  fixed inside the task.
- **A spec that is wrong, unclear or silent** where you need a decision → stop and ask. The spec is
  changed first (`write-specs`); never invent the rule, never edit a spec to fit the code.
- **Never weaken a test** to make it pass: no deleting, skipping, loosening, or marking expected to fail.
- Dependencies are added with the package manager's command (`npm install zod`, `uv add httpx`), never
  by typing a version into a manifest. A missing tool (a runtime, Docker) → stop; don't write code you
  can't run.
- **One check per command, with a timeout** (`timeout 300 npm test`), never chained or piped into
  `tail`: an implementer once waited half an hour on a hung check hidden inside a chain (D-043).
- A fresh database or service for a check is a throwaway one, on its own port, removed afterwards; never
  the developer's. Tests never call real outside services, and hold no secrets.

## Report, then wait

Before asking for the yes, tell the developer: per rule test, the failing assertion quoted from the red
run (or `RED: none` and why); the test and lint commands with their counts; the files changed; and every
planned or Notes item not done, or done differently, with the reason. A silently skipped item is a failed
task.
