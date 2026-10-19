# D-042 — Devflow's setup makes the project's tools ignore agent worktrees, and runs lint when the project has it

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: asked for in session on 2026-10-19.

**Context:** On devflow 0.16.1, Claude Code's agent worktrees under .claude/worktrees/ (its default, documented at code.claude.com/docs/en/worktrees, Grade 2) were swept by eslint . from the root, whose flat config ignored only dist and dev-dist; lint hung past 400 s, and git status showed ?? .claude/worktrees/, so merge.md's clean-tree check was always false. No devflow step ran lint: the reviewer did so on its own, and a backend had no linter.

**Options:** (a) worktrees outside the repository through a WorktreeCreate hook, which replaces Claude Code's worktree logic for every session with the plugin, drops .worktreeinclude and leaves agent worktrees uncleaned; (b) the setup proposes .claude/worktrees/ in .gitignore and in the root ignores of every linter, formatter and test runner; plus an optional per-app lint command that the gate, the reviewer and the merge run.

**Decision:** (b), the developer's call: the root lint config is to blame, and devflow adds the exception to ESLint and any other tool itself. Lint must not be a blocker when the developer does not want one; automated tests stay mandatory. A per-task diff before each merge (proposal 8) was refused.

**Trade-offs:** Tools devflow does not recognise keep sweeping the worktrees until someone adds the ignore. A project with lint configured pays its run on every commit that touches the app.
