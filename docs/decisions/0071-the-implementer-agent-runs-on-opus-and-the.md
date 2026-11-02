# D-071 — The implementer agent runs on Opus, and the evidence skill sets no model

**Status:** Accepted (2026-11-01).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-01, the quick-fix batch the developer asked for

**Context:** A review of the plugin on 2026-11-01 found agents/implementer.md on model: sonnet while the planner and reviewer ran on Opus, so the agent that writes all the code was the weakest; the developer had found the agents performing worse than the main session. skills/evidence/SKILL.md set model: sonnet, and the session-start pointer has every coding session invoke that skill, which can switch the session's model while it is active (hooks and skills reference, grade 3).

**Options:** (a) leave both; (b) the implementer on Opus and no model on the evidence skill; (c) every agent on the session's model.

**Decision:** (b), in the quick-fix batch the developer asked for ('make you quick fixes'). The implementer's code is what the reviewer then judges, so it gets the same model; the evidence skill runs on whatever model the session uses.

**Trade-offs:** An implementer run costs more than on Sonnet. Whether the model field of a skill really switched the session was not probed; it is removed either way.

**Changed by:**
- 2026-11-01 · dantelyro — by D-074: the implementer is removed, so its model no longer applies; the evidence skill still sets no model.
