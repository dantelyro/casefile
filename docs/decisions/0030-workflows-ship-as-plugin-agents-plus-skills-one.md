# D-030 — Workflows ship as plugin agents plus skills, one spec and one release each

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-14: "Code
review, Bug fix, Build from a plan, all 3 but each one in a different spec and version", with
write-specs added the same day, and "Design doc first".
**Implemented by:** `53e0e4c` — 2026-10-15 (`devflow:reviewer`), `cf02053` (`review`).

**Context:** The pilot project's milestone workflow — a planner, implementers in parallel worktrees, an
independent reviewer, merges after the developer's yes — worked through M0–M1 and is to become
general devflow workflows. Plugin agents cannot carry their own hooks or permission mode (ignored
for security), and a subfolder under `agents/` becomes part of an agent's name.

**Options:** (a) one large skill holding every workflow, its agents' prompts assembled at run time;
(b) plugin agents in a flat `agents/` folder (`devflow:<name>`) plus one skill per workflow, each
designed in its own spec and shipped in its own release, accepted only after real use on the pilot project;
(c) ship all workflows in one release.

**Decision:** (b). `review` (0.13.0), `fix-bug` (0.14.0), `implement` (0.15.0), `write-specs`
(0.16.0), each with a spec in `docs/specs/history/2026-10-14-*` and a plan before building. Agents are named
`devflow:<name>`, which is what hooks see in `agent_type`; every agent rule lives in the plugin's
`hooks/hooks.json`, branching on it. A skill dispatches its agents by name, so no trigger matching
stands between a workflow and its agents.

**Trade-offs:** Four releases instead of one, each waiting for its the pilot project test before the next
builds on it. A workflow skill whose description overlaps a built-in skill (`review` and
`code-review`) needs trigger evals, which are billed and run on demand.
