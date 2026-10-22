# D-055 — Trigger evals explicitly opt out of session-start context

**Status:** Accepted (2026-10-22).
**Decided by:** dantelyro — Grade 1: approved Add the eval-only opt-out (Recommended) in the 2026-10-22 session

**Context:** M4 T1 observed SessionStart firing during Claude plugin eval, so a forced evidence skill invocation contaminates EVID-001 and EVID-002 trigger checks (B1). The developer approved Add the eval-only opt-out in this session on 2026-10-22. The eval documentation permits EVAL_ environment keys.

**Options:** (a) Explicit EVAL_ flag disabling session-start context for selected cases; (b) weaken graders to ignore skill exclusion; (c) keep trigger rules manual.

**Decision:** Only EVAL_DEVFLOW_SKIP_SESSION_START=1 makes session_start emit nothing. EVID-001 and EVID-002 trigger cases set it explicitly. Other values preserve normal context; no guard consults this flag. EVID-006 tests the opt-out.

**Trade-offs:** The trigger cases isolate request matching and do not test normal startup integration, which remains covered by session-start tests and its probe. The flag must be opted into explicitly.
