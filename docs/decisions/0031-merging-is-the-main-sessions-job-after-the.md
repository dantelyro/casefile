# D-031 — Merging is the main session's job, after the developer's yes for each change

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: the 0.14.0 spec
(`docs/specs/history/2026-10-14-fix-bug-design.md`) was approved in session on 2026-10-14; the practice is
The pilot project M0–M1's, where every merge waited for the developer's OK.
**Implemented by:** `e2e4113` — 2026-10-15 (`shared/merge.md`), with the implementer's and
reviewer's guard rules (`65adde2`).

**Context:** In the pilot project's milestone workflow an implementer works in its own worktree and a reviewer
approves, but neither merges: the orchestrating session showed the developer one line per change and
merged only after a yes. M1 showed why the merge is a step of its own — a green suite once passed with
a broken web image (M1/F1), and two suites sharing one test database failed each other at commit.

**Options:** (a) the implementer merges its own approved branch; (b) the reviewer merges on approve;
(c) the main session merges, one change at a time, after the developer's explicit yes for that change.

**Decision:** (c). Agents never merge — the guards refuse `git merge`, `rebase`, `cherry-pick` and
switching to the default branch to the implementer, and every git change to the reviewer. The merge
follows `shared/merge.md`: proven on the default branch (tests, the app's image when touched), the task
or issue status recorded in the merge commit, then every worktree the change used cleaned up.

**Trade-offs:** The developer answers once per change, even in a batch of three parallel tasks. A yes
for one change never carries to the next, so an unattended run stops at every merge.
