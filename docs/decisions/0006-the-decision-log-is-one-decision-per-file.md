# D-006 — The decision log is one decision per file, from entry one

> **Reconstructed entry (2026-08-27).** Written from the body of `cc71194`, which records the
> reasoning and both war stories contemporaneously. This is the author's reasoning as committed,
> not an inference from the diff. The 886-line figure is theirs.

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `cc71194`, the `fix`
commit that made the layout unconditional. Co-authored with Claude Opus 5; the human author is
named because the agent proposes and a human accepts.
**Implemented by:** `cc71194` — 2026-08-27.

**Context:** The skill previously prescribed a single log file with "split when it exceeds ~500
lines". Seeding a real backend log exposed the defect: a conditional layout requires someone to
stop, measure, and choose migration over the task in front of them. Nobody does. One real log
reached **886 lines** before anyone split it, by which point it was read with `grep` and line
ranges rather than opened — the exact failure the threshold existed to prevent.

**Options:** (a) keep the threshold and raise its prominence; (b) keep one file permanently and
accept `grep`-scale reading; (c) `docs/decisions/NNNN-slug.md` from entry one, with a generated
`README.md` index carrying id, title and status only.

**Decision:** (c), unconditional. The `next id` pointer is dropped entirely — the highest
filename is the pointer, so there is no shared line to contend over. `decisions/` is a
**sibling** of `architecture/`, never nested inside it: the architecture document says what
exists and where, the log says why and what was given up, and the log also covers scope and
product choices no architecture document describes. Two rules carried over from practice:
supersede on the `Status` line, because a reader opens one entry alone and never sees a banner
below the fold; and superseded entries stay under their original filename, since moving them
breaks every `see D-NNN` aimed at them.

**Trade-offs:** Cross-references now cost a relative link resolved through the index, and the
index is a second artefact that can fall out of step with the directory. Accepted because the
index holds no reasoning — only what can be regenerated from filenames and `Status` lines.

**The wider lesson, which outlives this entry:** a rule conditional on someone noticing a
threshold is not a rule. If the migration is the same work either way, do it at entry one.
