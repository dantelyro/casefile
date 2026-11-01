# D-070 — Project context reaches every agent through a SubagentStart hook, not through agent prompts

**Status:** Accepted (2026-11-01).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-01, in the developer's words quoted above

**Context:** M7 put 'read the decision index and every decision touching your work' into the prompts of the planner, implementer and reviewer (PLAN-001, IMPL-004, REV-010). Only casefile's three agents got it, and the same instruction sat in three prompts. The developer: 'i thought you would run this hook on them or separete the hook in two so they get the docs part only and you the behaviral hook like reconcile docs'. The hooks reference (grade 3) says SubagentStart additionalContext goes into the subagent's context before its first prompt; a live probe on Claude Code 2.1.312 (2026-11-01, grade 1) showed a plugin agent and the built-in Explore agent both recite a word injected only by a SubagentStart hook, and the main session not see it.

**Options:** (a) keep the reading in each agent prompt; (b) one hook text for everyone, the evidence pointer included; (c) split session_start: project context for the main session and every agent (SessionStart and SubagentStart), the evidence pointer for the main session only, and each role's reaction to a contradiction kept in its prompt.

**Decision:** (c), the developer's split, for every agent ('yes every agent'). Agents never get the evidence pointer: reconciling docs and recording decisions need the developer, whom an agent cannot ask. PLAN-001, IMPL-004 and REV-010 keep only what each role does with the decisions; CTX-001 and CTX-002 state what everyone is told.

**Trade-offs:** Every agent spawn, casefile's or not, pays a few hundred tokens for the context. An agent unrelated to the project's code (a docs lookup, say) gets it too. Without Python the starter answers SubagentStart with the SessionStart-shaped install message, whose mismatched event name Claude Code presumably reports as a hook notice (not checked); SubagentStart cannot block, so nothing stops.
