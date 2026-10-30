# D-063 — The claim-audit milestone is dropped; a full read of the docs is done on request

**Status:** Accepted (2026-10-29).
**Decided by:** dantelyro — Grade 1: in session on 2026-10-29

**Context:** Milestone M6 (specified 2026-10-28 in 1b7d739 and 42fa68d, its proposal then numbered D-062) added a stdlib script, claims_check.py, run at every reconciliation to flag cited decisions, paths and Claude Code versions that no longer hold, plus a full audit on request. After one task merged (T5) and T1 failed review twice, the developer had lost track of it.

**Options:** (a) finish M6; (b) keep only the on-request audit as skill prose; (c) drop it and ask for an audit when wanted.

**Decision:** (c), the developer's call on 2026-10-29: 'cant i just aske to find false claims?', then 'delete everything on M6'. Asking 'find false claims and outdated docs and fix them' does the job without a ~200-line script and four more tasks, which fits the simplification direction. Specs, plan, product decisions and merged code were removed in 8b25c33; the proposal's entry was deleted rather than superseded, so its number, D-062, was reused.

**Trade-offs:** Nothing checks the docs unless the developer asks; a spinner tip on the developer's machine reminds them. The script would have caught broken references mechanically at every reconciliation; a request depends on remembering. The deleted entry survives only in git history (1b7d739).
