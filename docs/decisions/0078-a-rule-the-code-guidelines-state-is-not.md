# D-078 — A rule the code guidelines state is not repeated in a skill; skills keep their own procedure, and the reviewer keeps its copies

**Status:** Accepted (2026-11-02).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-02, in the developer's words quoted above

**Context:** D-076 put general code rules in the session-start guidelines. Skills and shared files repeated several of them: a bug found along the way is left (build-task, implement), never weaken a test (build-task), stop and ask instead of improvising (implement), no secrets, no dependence on test order, do not guess the branch. build-task's refactor step conflicted with the guideline to ask before refactoring. CLAUDE.md already says to state each rule once, in the place it applies (D-008).

**Options:** (a) keep both copies; (b) remove the skill's copy wherever a guideline states the rule; (c) remove the guideline's copy and keep the rules in the skills.

**Decision:** (b), the developer asked 'if a guideline already enforces it the skill does not needs too?', then 'you may clean up'. A skill keeps what is its own: the procedure (issue to fix-bug, branch names, rule-ID test names, RED on an assertion, the Reuse: line) and reasons that carry project knowledge. The reviewer agent keeps every rule, because no agent gets the guidelines (D-074). build-task's refactor step is limited to the code just written, which needs no question. The guideline on existing tests (ask before changing or deleting one) replaces build-task's 'never weaken a test'.

**Trade-offs:** The skills now depend on the guidelines being injected: a future switch to turn the guidelines off in a project would leave those rules unstated there. The reviewer and the guidelines can drift apart, since they hold separate copies.
