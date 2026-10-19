# D-046 — Tests for existing code are specified by write-specs and built by implement; there is no separate test-writing skill

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-19: "write-spec will also write spec about test only spec. just like it does with the rest so that means i dont need a write-test skill?", and "yes write it".

**Context:** Adding tests to an existing codebase had no devflow path. On devflow 0.16.1 a milestone of tests for existing screens went through implement as ordinary tasks, and broke only on the missing red and the unrun breaks (D-045). Every devflow test is named after a spec rule (D-034), and existing code usually has none; behaviour read off code shows what it does, never what it must do.

**Options:** (a) a write-tests skill with the implementer, planner and reviewer loop; (b) a write-tests skill where the main session writes the tests and the reviewer proves them, naming tests with no rule after their behaviour; (c) write-specs drafts rules from the existing code, each proposed, and implement builds them as tests-only tasks.

**Decision:** (c), the developer's call. write-specs reads the named scope and drafts one rule per observed behaviour, each shown as proposed; behaviour that looks wrong is never drafted as a rule but asked at the approval step, and becomes a rule or an issue. The milestone holds tests-only tasks, proved by the reviewer's breaks. D-035 is unchanged: the main session never writes tests.

**Trade-offs:** Adding a few tests to one module takes specs, a plan and agents, the weight of any feature. write-specs' description gains a second kind of input, which changes when it triggers and needs eval cases.
