# D-057 — The session-start pointer waits for the first change, in one output form

**Status:** Accepted (2026-10-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-27, in the developer's words quoted under Context.

**Context:** On 2026-10-27 the hook made Claude load the evidence skill and face 20 unreconciled commits before answering a conceptual question about RAG; none of it was used. The developer also dropped agent-agnostic support ('i though agents had more similarities and that is not the case'), leaving session_start's top-level output form and COPILOT_CLI check without a user. Asked to apply the recommended changes: 'can you do all? and test then yourself?'

**Options:** (a) keep 'invoke now, before your first response'; (b) invoke before the first change to code or docs; (c) drop the hook and rely on the description. For the output: keep both forms, or emit only the nested one.

**Decision:** (b), and only the nested form. The pointer tells Claude to invoke the skill before changing any code or document, and that a session that only asks, explains or plans does not need it. session_start always emits hookSpecificOutput.additionalContext.

**Trade-offs:** The trigger now depends on Claude judging when a change starts, which a pointer can misjudge; trigger evals (evals/evidence-*) measure it. A non-Claude-Code agent that reads only the top-level field gets nothing. (c) would lose reconciliation entirely, since no description can match a session start (D-003).
