# D-007 — `Decided by` is resolved from blame, never from `git config`

> **Reconstructed entry (2026-08-27).** Written from the body of `cc71194`, which records the
> incident and the reasoning contemporaneously. The 16-entry / 18-commit figures are the
> author's.

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `cc71194`, the `fix`
commit that replaced the attribution procedure. Co-authored with Claude Opus 5; the human author
is named because the agent proposes and a human accepts.
**Implemented by:** `cc71194` — 2026-08-27.

**Context:** The skill documented `Decided by` as `git config user.name`, licensed by the
inference "not the agent, so the git identity is the right one". Seeding a real backend log put
the requester's name on all **16** entries; blame showed they had authored none of the **18**
commits, and the real deciders were two entirely different people. The field read as first-hand
throughout, which is what made it dangerous.

**Options:** (a) keep `git config` and add a caveat that it may be wrong; (b) drop the field,
since an unreliable name is worse than none; (c) resolve it from `git log -L` over the lines the
decision governs, filtered to `feat`/`fix`.

**Decision:** (c). `refactor` is a second pass, since a refactor is as often a move that decided
nothing. Repos without conventional prefixes — most of them — read subject lines instead, and the
reference carries worked examples of the judgement call, including the mixed subject and the
sweeping mechanical change that touches every line range and decides nothing. Attribution gets
its own evidence ladder, with `git config` and sole-committer inference at Grade 4.

**Trade-offs:** Attribution now costs a command and a judgement call per entry, and on a repo
with unhelpful commit subjects it can fail to produce a name at all. That is the intended
outcome: a blank field beats a confident wrong one. A single-contributor repo does not make its
one contributor the decider of everything in it.

**The wider lesson, which outlives this entry:** a procedure that always produces a
confident-looking answer is suspect precisely because it never fails.
