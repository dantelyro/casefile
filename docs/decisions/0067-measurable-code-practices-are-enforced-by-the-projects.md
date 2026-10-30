# D-067 — Measurable code practices are enforced by the project's linter through a Stop hook

**Status:** Accepted (2026-10-29).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-10-29, in the developer's words quoted under Context

**Context:** Prose alone did not stop single-letter names and unreadable code (the developer, quoted in D-066). Names, complexity, nesting, function length and magic numbers can be measured by ESLint and ruff rules. The hooks reference documents that a Stop hook blocks the end of a turn with decision: block and a reason, that Stop fires in the main session only (subagents fire SubagentStop), and that onFailure has no effect on Stop (grade 3, fetched 2026-10-29). Asked whether to lint every turn with uncommitted changes or only what changed during the turn, the developer: 'lint only when changed'.

**Options:** (a) a Stop hook running each changed app's lint, blocking on failure; (b) a PostToolUse hook linting after every edit; (c) leave lint to the reviewer only.

**Decision:** (a). The skill proposes the stack's linter rules and writes them after a yes; the Stop hook runs the lint of each app whose files changed during the turn, measured against the state when the previous turn ended or the session started, blocks with the lint output on failure, never blocks again on a retry, and never blocks with nothing to lint (PRAC-009..012). Agents are covered by the reviewer, which already runs lint.

**Trade-offs:** Lint runs at most once per turn, so a failure surfaces at the end of the turn, not at the edit. The hook must remember each app's state between turns. stop_hook_active is unverified (PRAC-011 [VERIFY]). A Stop hook cannot fail closed.
