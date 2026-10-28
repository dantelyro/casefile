# D-061 — Reconciliation replays the watermark gap's log, with a diff as a cross-check

**Status:** Accepted (2026-10-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-27, in the developer's words quoted under Context.

**Context:** Supersedes D-058, which replaced replaying git log with git diff --stat because the eb7f238..HEAD gap held all of M4 and its revert. That reasoning generalised from an outlier: the watermark moves with every doc update, so the gap is normally a few commits and replaying them is cheap, while the diff hides how the code got where it is — what was tried, what was reverted and why — which is what the docs and the decision log exist to record. The developer, after approving D-058: 'how it got there is way more important and it is cheap it kept updated'; then 'yes go ahead'.

**Options:** (a) keep D-058: git diff --stat, git log only per file; (b) plain git log --oneline, as before D-058; (c) git log --oneline as the main step, a revert read together with the commit it undoes as one item, then git diff --stat over the same range as a cross-check.

**Decision:** (c), in SKILL.md, references/living-documents.md and the session-start pointer. D-058's date fallback stays, replaying from the last commit before the watermark's date.

**Trade-offs:** A large gap, such as a reverted milestone, costs more reading than the diff did; pairing each revert with its commit keeps that to one item per attempt. The cross-check costs one extra command.
