# D-066 — Code practices are one stack-scoped skill shared by the main session and the agents

**Status:** Accepted (2026-10-29).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-10-29, in the developer's words quoted under Context

**Context:** The developer asked for best practices that sessions follow, researched into a guide (the Code Practice Field Guide artifact). A file read only by the agents was proposed first; the developer: 'yeah but those are for the agents only i also want the main session to follow those', and 'i want as a rule you will match the best practices for whatever we are building no more than that you dont need react best one if we are working with node'. Against leaving out rules the model already knows: 'you said you already have most of those and still like to make unreadble code and single letter variables'. An invoked skill is re-attached after compaction (first 5,000 tokens); a file read with Read is not (docs/skill-authoring.md, grade 3).

**Options:** (a) a shared file only the agents read; (b) one skill, pointed to by the session-start hook and preloaded by the agents, with a short stack-independent body and one reference per stack; (c) the rules in an output style with force-for-plugin; (d) a block in each project's CLAUDE.md.

**Decision:** (b), the skill casefile:code-practices. Its body holds stack-independent do/don'ts under 150 lines; Node, React, Vue and Python each have a reference, plus a shared backend and a shared frontend file, read only for the stack of the changed code (PRAC-001..009). The project's own CLAUDE.md, linter config and design system win.

**Trade-offs:** A skill is guidance the session can drift from; D-067 enforces what a linter can measure. Every session that changes code pays for the body. Whether plugin agents resolve a namespaced skill in their skills field is unverified (PRAC-007 [VERIFY]).

**Changed by:**
- 2026-10-31 · dantelyro — a live probe on Claude Code 2.1.312 showed a plugin agent with only the
- 2026-11-01 · dantelyro — by D-074: of casefile's agents only the reviewer is left, so the skill is shared by the main session and the reviewer.
  Read tool recite a word found only in a skill its `skills` field named as `<plugin>:<skill>`
  (grade 1), so the agents preload `casefile:code-practices` and PRAC-007 is no longer `[VERIFY]`.
