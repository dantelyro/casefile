# D-084 — Tests are announced to the developer before they are written, and only meaningful ones are made

**Status:** Accepted (2026-11-20).
**Decided by:** dantelyro — Grade 1: stated in this session on 2026-11-20

**Context:** While building D-083 (a rule ID goes in a comment), the session added a test per language and per variant for what is a plain convention, without saying which tests it would write. The developer objected: a simple behaviour change like that needs no new tests, and they want to see which tests are made, and why, before any is written.

**Options:** (a) a personal memory of the developer's preference; (b) a line in casefile's code guidelines, which the session-start hook gives every session; (c) a step in shared/build-task.md, which reaches only implement and fix-bug.

**Decision:** (b), the developer's call on 2026-11-20: 'this is another thing to add to casefile', with the wording approved in this session. The guidelines reach every session, with or without a skill, and a rule the guidelines state is not repeated in a skill. Before writing a test, the session names each test and the behaviour it proves and waits for a go, and writes only tests that fail when a behaviour breaks. The rule is stated generally: a first draft named this session's case (one test per language) and was cut, since the guidelines apply to every project.

**Trade-offs:** One more stop before the red step of every task, on top of the brief (D-079). Which tests are meaningful is the session's judgement, which the developer checks when the list is announced.
