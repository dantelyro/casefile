# D-058 — Reconciliation diffs the watermark gap instead of replaying the log

**Status:** **SUPERSEDED by D-061 (2026-10-27)** — the diff hid how the code got where it is, and the gap it was meant to shrink is normally a few commits.
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-27, in the developer's words quoted under Context.

**Context:** The gap from this repo's watermark eb7f238 to HEAD held all of M4 and its revert (D-056): replaying git log meant reviewing dozens of commits whose net effect was a handful of files. The developer accepted the change on 2026-10-27: 'can you do all?'

**Options:** (a) git log --oneline <watermark>..HEAD, then read each commit; (b) git diff --stat <watermark>..HEAD, then read the changed files, with git log only for why a file changed.

**Decision:** (b), in SKILL.md, the session-start pointer and references/living-documents.md. The date fallback for an unresolvable SHA diffs from the last commit before that date.

**Trade-offs:** The diff hides intermediate states and the commit that explains each change, so finding why takes a second command. A revert no longer costs a review.

**Changed by:**
- 2026-10-27 · dantelyro — superseded by D-061; generalised from the M4 revert, an outlier gap, and lost the history the docs record.
