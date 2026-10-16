# D-035 — The orchestrator never writes product code, tests or specs; the plan file is the progress record

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: approved with the 0.15.0 spec
(`docs/specs/2026-10-14-implement-design.md`) on 2026-10-14.
**Implemented by:** `9d894b4` — 2026-10-15 (`plan_status.py`), `2a03d6c` (`devflow:planner`),
`2d64684` — 2026-10-16 (`implement`).

**Context:** In Inverso M0/M1 the main session ran a milestone: it dispatched implementers and
reviewers, merged, and kept the plan. Its own context filled with diffs when it read them, and when it
filled a spec gap with its own wording ("≤4 words is reasonable") the builder failed the task twice
(M1/T3). Sessions also ended mid-milestone, and the next one had to find out what was done.

**Options:** (a) the main session also fixes small things itself; (b) the main session only
orchestrates — agents write code and tests, the developer decides spec gaps — and progress lives in
the plan file; (c) progress kept in a separate state file or in the session.

**Decision:** (b). `implement` coordinates agents and keeps the plan; it never writes product code,
tests or specs. Code and tests come from `devflow:implementer`, verdicts from `devflow:reviewer`, the
plan from `devflow:planner`; a spec gap is asked, the spec amended first, and the task carries the
exact rule. It passes paths and IDs to agents, never file contents, and does not read full diffs. The
plan file in `docs/plans/` is the single record of progress: each task's `Status:` line, read by
`plan_status.py` for the next batch and for tasks stuck `in-progress`, which is how a later session
resumes.

**Trade-offs:** A one-line fix still goes through an implementer and a review round. The plan's
statuses are only as true as the orchestrator keeps them: an `in-progress` task may hide a finished,
unreviewed commit, so resuming checks the task's branch before discarding anything. Nothing but the
skill's own instructions stops the main session from editing code — the planner's and the reviewer's
limits are hooks (D-030), the orchestrator's are not, because it is the developer's own session.
