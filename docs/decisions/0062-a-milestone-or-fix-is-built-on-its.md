# D-062 — A milestone or fix is built on its own branch, which the developer merges

**Status:** Accepted (2026-10-29).
**Decided by:** dantelyro — Grade 1: asked for in session on 2026-10-29, after dropping M6

**Context:** Every task and fix was merged into the default branch as soon as it was approved. Dropping the claim-audit milestone (M6) on 2026-10-29 took a hand-made revert of specs, a decision, product decisions, a plan and merged code (8b25c33). The developer also lost track of what was being built: each change landed on main through a worktree they never saw.

**Options:** (a) keep merging into the default branch; (b) a feat/ branch per milestone and a fix/ branch per bug, cut from the default branch, which the developer merges or deletes; worktrees kept for every implementer; (c) as (b), with implementers working directly on the branch unless the developer chooses parallel tasks.

**Decision:** (c), the developer's call: 'i will merge back to main not you, branch is created at implement, bug fix is just a branch change'. implement and fix-bug propose the branch name and ask the developer, with alternatives and a free-text answer, 'so the dev dont loose track on what he is working'; siblings get a branch of the same name. implement asks for the mode: task by task (one implementer, no worktree, on the feat/ branch) or parallel (worktrees merged into the feat/ branch by shared/merge.md). A fix is never built in a worktree. The reviewer keeps its own worktree in every case, because it breaks code on purpose. The implementer's fixed isolation: worktree is removed; parallel dispatches ask for one. A probe on 2026-10-29 confirmed an agent dispatched without isolation works in the session's checkout and branch (Grade 1). issues_status.py checks a fixed issue against the current branch, since the fix is not on the default branch until the developer merges it.

**Trade-offs:** Task by task leaves the checkout busy while an implementer works in it, and a rejected task's commits are already on the branch, to be reverted rather than discarded. Issue and decision numbers come from the files on the current branch, so two open branches can hand out the same number; work-branch.md has the developer check before merging. Nothing gets to the default branch until the developer merges, so a later milestone may start from a default branch without the earlier one.
