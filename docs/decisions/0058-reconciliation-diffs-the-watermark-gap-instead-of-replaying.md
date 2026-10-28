# D-058 — Reconciliation diffs the watermark gap instead of replaying the log

**Status:** Accepted (2026-10-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-27, in the developer's words quoted under Context.

**Context:** The gap from this repo's watermark eb7f238 to HEAD held all of M4 and its revert (D-056): replaying git log meant reviewing dozens of commits whose net effect was a handful of files. The developer accepted the change on 2026-10-27: 'can you do all?'

**Options:** (a) git log --oneline <watermark>..HEAD, then read each commit; (b) git diff --stat <watermark>..HEAD, then read the changed files, with git log only for why a file changed.

**Decision:** (b), in SKILL.md, the session-start pointer and references/living-documents.md. The date fallback for an unresolvable SHA diffs from the last commit before that date.

**Trade-offs:** The diff hides intermediate states and the commit that explains each change, so finding why takes a second command. A revert no longer costs a review.
