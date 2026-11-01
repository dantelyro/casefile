# D-065 — The planner checks every milestone against the decision log and the codebase

**Status:** Accepted (2026-10-29).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-10-29, in the developer's words quoted under Context

**Context:** No agent read the decision log: the planner read the build order, specs, plans and code; the implementer and reviewer read only CLAUDE.md. A milestone that brought back dropped work, or rewrote a helper that already existed, would be planned without a word. The developer: 'when i build something that like was already remove and dropped will the planner understand that im breaking something? will the planner understand that some the code base has code that can be reused?', then 'the planner is the most important one to know those things'.

**Options:** (a) write-specs checks a feature against dropped and superseded decisions before drafting; (b) the planner reads the history and the code, and blocks dropped or contradicting work, with the implementer and reviewer as follow-up checks; (c) every agent reads the whole decision log.

**Decision:** (b). The planner reads CLAUDE.md, product-decisions.md, open-questions.md, the decisions index and every decision touching the milestone, lists them under History checked:, puts work that revives dropped work or contradicts a decision under Blockers, and names reusable code on each task's Reuse: line (PLAN-001..004). The implementer uses what Reuse: names (IMPL-003); the reviewer flags duplication and contradicted decisions (REV-009). write-specs is unchanged: one gate, in one place.

**Trade-offs:** A revival is caught at planning, after its specs are written, not before; (a) would catch it earlier but puts the check in a second place. Planning reads more and costs more tokens. The rules are agent prose, tested by hand ([MANUAL]).

**Changed by:**
- 2026-10-29 · dantelyro — the planner is no longer the only gate: the implementer and the reviewer
  also read the decisions touching their task or change (IMPL-004, REV-010). The developer: 'so if the
  implent can still contradict too all agents should know about it'.
- 2026-11-01 · dantelyro — the reading moved from the three agent prompts to a SubagentStart hook that
  gives every agent the project context; each role keeps what it does with a contradiction (D-070).
