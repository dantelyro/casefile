# D-033 — Bugs are issues in `docs/issues/`, fixed on their own branch; a blocking bug blocks by reference

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session on 2026-10-14 — every
bug is fixed on its own branch, the status names kept as written, `issues_status.py` wanted — and
approved with the 0.14.0 spec the same day.
**Implemented by:** `311c022` — 2026-10-15 (`issues_status.py`), `3d20030` (`fix-bug`), `3da075e`
(`docs/issues/` protected from agents).

**Context:** Inverso M1 fixed bugs as `F<n>` tasks appended to the milestone's plan (F1–F3). Bugs
found while building a feature are of two kinds: unrelated to it, or in merged work the next task
builds on, so the task cannot proceed until the bug is fixed.

**Options:** (a) bugs as tasks in the plan they were found in, as in M1; (b) bugs fixed inside the
feature's branch; (c) one file per bug in `docs/issues/`, fixed on its own branch, a blocking bug naming
the task it blocks in `Blocks:`.

**Decision:** (c). An unrelated bug is filed and the feature continues; a blocking bug's fix is merged
first and the task waits for it, by reference, never by sharing a branch. A bug inside a task's own
unmerged branch is a review finding, not an issue. Agents report bugs in `NOTES` and never write issues
(the file guard refuses it); the main session files them after the developer agrees. `issues_status.py`
checks every `fixed` issue against the repository instead of believing its status line.

**Trade-offs:** A blocking bug adds a merge before the task it blocks. Issues live outside the plan, so
`implement` (0.15.0) has to read `Blocks:` to keep blocked tasks out of a batch. `issues_status.py`
checks that the named test exists, not that it passed — devflow keeps no record of test runs; passing
is shown at merge.
