# D-081 — Every session warns before acting on a request that conflicts with a decision or spec rule

**Status:** Accepted (2026-11-19).
**Decided by:** the developer — Grade 1: asked in session on 2026-11-19

**Context:** The session-start context told the session to say so when its own work would contradict an accepted decision. That line was there and still failed: a session proposed changing what an accepted decision settled without warning, and later told the developer that casefile had no such warning at all. It said nothing about the developer's own requests, nor about spec rules: in a project, a request that went against a spec rule (when the CPF/CNPJ is required) was not flagged. The developer asked for a conflicting-decisions warning, 'this is extremelly important'.

**Options:** (a) a rule in shared/build-task.md, for implement and fix-bug only; (b) the session-start context, which every session gets.

**Decision:** (b). When a request, the developer's own included, or anything the session proposes or builds would contradict an accepted decision or a spec rule, or revive dropped work, the session stops before acting and warns: it names the decision or rule, says what it says and how the request conflicts, and asks whether to change it first or drop the request. Nothing is built around it or followed silently; the spec or decision changes first, then the code.

**Trade-offs:** A few more tokens in every session's context, and one more round-trip whenever a request touches a settled rule.
