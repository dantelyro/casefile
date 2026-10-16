# D-036 — A task that conflicts at merge is redone from the default branch, never resolved in place

**Status:** Accepted (2026-10-16).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: chose option A in session on
2026-10-16, after the 0.15.0 live run.
**Implemented by:** `6c2bbf8` — 2026-10-16 (`shared/merge.md`, `implement`, `devflow:implementer`).

**Context:** In the 0.15.0 live run on an Inverso M2 clone, T2 and T12 both changed
`worker/pyproject.toml` and its lock file, so T2's branch conflicted with `main` once T12 was merged.
The skill said to stop and ask; instead the orchestrator ran `git merge --no-commit main` inside T2's
worktree and had the implementer finish the merge, which went around the guard that keeps
implementers from merging (D-031).

**Options:** (a) stop and ask; on a yes, a new implementer redoes the task from the current default
branch, reusing the old branch's work, and it is reviewed again; (b) on a yes, the implementer merges
the default branch into its own branch, the guard loosened for that one case; (c) the developer
resolves the conflict.

**Decision:** (a). `merge.md` aborts the merge, names the conflicting files and stops. With the
developer's yes, `implement` dispatches a new `devflow:implementer` with `Redo <plan> <task> from
<branch>`: its worktree starts from the default branch, it reads the old commits with `git show` and
writes the work again, adding dependencies with the package manager so lock files are regenerated,
not merged. The result goes through review and its own fix rounds as a new one. Nobody runs git in an
agent's worktree, and the guard is unchanged — implementers still may not merge, rebase or
cherry-pick.

**Trade-offs:** A redo costs a full implementer and reviewer run, even when the conflict is one
line of a lock file. The redo writes the work again by hand, so it can drift from what was reviewed;
the second review is what catches that.
