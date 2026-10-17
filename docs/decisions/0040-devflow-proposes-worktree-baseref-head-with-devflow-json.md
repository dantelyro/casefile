# D-040 — Devflow proposes worktree.baseRef head with devflow.json

**Status:** Accepted (2026-10-17).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: asked for in session on 2026-10-17, after it showed on the portfolio project.

**Context:** Agent worktrees branch from the remote unless `worktree.baseRef` is `"head"`, and devflow never pushes; on the portfolio project the first implementer started without the specs or the plan. A plugin cannot set it: plugin settings keep only `agent` and `subagentStatusLine` (code.claude.com/docs/en/plugins/components.md, Grade 2). Inverso had it from before devflow, which hid the gap in every live test.

**Options:** (a) a README note; (b) a script that checks the setting before each dispatch; (c) the step that proposes `.claude/devflow.json` proposes the setting in `.claude/settings.json` with it, under the same yes.

**Decision:** (c), the developer's call: "its just flag devflow should set". `review` proposes both; `implement` and `fix-bug` propose whatever is missing before dispatching.

**Trade-offs:** Only the project's settings file is checked, not the developer's own; a setting written mid-session may need a restart.
