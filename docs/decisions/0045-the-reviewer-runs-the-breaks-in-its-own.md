# D-045 — The reviewer runs the breaks in its own worktree; the implementer no longer proves its own tests

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-19: "i think this is not implementer role", "why reviewer should not also be the breaker? how diferente can he be?", the reviewer does not commit, and "yes write it" for the spec.

**Context:** Every proof that a test can fail was run by the agent that wrote the test. In the 0.15.0 live run 2 of 10 breaks made by hand survived the suites, and two of three reviewers only reasoned about breaks. On devflow 0.16.1 a milestone that only added tests for existing screens had no red at all, so the breaks were its only proof; the reviewer's hooks blocked every edit, and when an implementer was stopped without a report nobody had run the second round's breaks.

**Options:** (a) the implementer runs its own breaks, as it stood; (b) a separate breaker agent between the implementer and the reviewer; (c) a breaker as a context: fork skill, editing the developer's checkout with no worktree and an undocumented agent_type; (d) the reviewer runs the breaks in its own worktree, restores them, and still never commits.

**Decision:** (d), the developer's call. The implementer writes tests and code; the reviewer breaks the code under each rule's main test and its own edge cases, quotes each result, restores with git restore and ends with a clean git status. A break that stays green is a major finding. guard_paths lets the reviewer edit only inside a linked worktree and never a test file; guard_bash adds git restore without --staged or --source. A task whose behaviour already exists reports RED: none, accepted only when it touches no product code. Rules: REV-001 to REV-008 (docs/specs/20-reviewer.md), IMPL-001 and IMPL-002 (21-implementer.md), GUARD-001 to GUARD-004 (10-guards.md).

**Trade-offs:** The reviewer is no longer strictly read-only, so its limits move from 'never edits' to a path rule a hook must get right. A break left unrestored only breaks the reviewer's own throwaway worktree, never the merged branch. Review rounds take longer, since breaks are run instead of reasoned about.
