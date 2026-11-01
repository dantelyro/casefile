# D-073 — No reference to worktrees is left in the plugin

**Status:** Accepted (2026-11-01).
**Decided by:** dantelyro - Grade 1: decided in session on 2026-11-01, in the developer's words quoted above

**Context:** D-072 removed worktrees from every flow in 0.28.0, but the plugin still carried them: lib.repo_relative mapped a path under .claude/worktrees/<agent>/ to the repo path, the guard tests built real linked worktrees for the reviewer and the implementer, and the skills, agents, specs, README and CLAUDE.md said 'without a worktree' at every dispatch. A test review in session found the worktree tests testing an arrangement that no longer exists.

**Options:** (a) keep the mapping and the negations as a guard against worktrees coming back; (b) remove every reference: the mapping, its tests, the worktree fixtures and the 'without a worktree' wording.

**Decision:** (b), the developer's call: 'there is no more worktrees so this plugin have to remove all references on that.' The .claude/worktrees/ path mapping and its tests are gone; the reviewer's GUARD-002 and GUARD-003/005 tests run in a plain checkout; skills, agents, specs, README, CLAUDE.md and product-decisions no longer mention worktrees; the .gitignore entry is dropped. The reviewer's restore allow-list (GUARD-003) also loses -W/--worktree, git restore's flag for the working tree: it is what git restore <path> does by default, so it was redundant ('remove the redundant'). Kept: --staged --worktree in the orchestrator's git restore in implement, which needs both to bring back saved work; isolation in skill-authoring.md's list of supported agent fields; and history - decision entries, docs/specs/history/, docs/plans/ and M11's name in the build order - which record what was true then.

**Trade-offs:** A path under .claude/worktrees/ is now just a path under .claude/, which every agent is refused. Nothing in the prompts tells the orchestrator not to pass isolation: worktree when it dispatches an agent; the default is no isolation and the agents set none.
