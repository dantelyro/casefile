# D-011b — The doc set gains a requirements document

**Status:** **SUPERSEDED by D-023 (2026-09-14).** `docs/requirements.md` is not something
`evidence-based-decisions` can source from a repo, so it is no longer part of the set this skill
proposes, seeds or reconciles. The document itself survives — `mvp` owns it, and the `F-NN`/`N-NN`
format below moved to `skills/mvp/references/documents.md` intact. Accepted (2026-08-27). Since
D-026 (2026-10-14) `mvp` is removed with nothing migrated: no skill owns `docs/requirements.md`, and
the format below survives only in this entry.
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: requested directly in session.
**Implemented by:** `b2f8cd5` — 2026-08-27.

**Context:** The set covered how to run it, what exists, and why it is that way. It had nothing for
what the project *must do*, so "done" had no definition to test against.

**Options:** (a) fold it into the architecture document; (b) a new member of the set.

**Decision:** (b). `docs/requirements.md` — functional `F-NN` and non-functional `N-NN`, with stable
ids so decisions and tests can cite them, and a number on every non-functional one. It sits above
the architecture document in the seeding order, beside `docs/purpose.md` (**D-011**).

**Trade-offs:** One more document to keep true, and requirements rot faster than anything else in
the set. Mitigated only by the same non-overlap rule the others follow — requirements hold no
design.

**The wider lesson, which outlives this entry:** an unnumbered non-functional requirement cannot be
violated, only disappointed. "Fast" is not a requirement. This survives the supersede — it moved to
`mvp` with the format, because it was never a claim about which skill owns the document.

**Changed by:**
- 2026-09-14 · dantelyro — split out of D-011, which had decided purpose and requirements together
  under one id. Filed as `0011b` per the log's insertion convention, so no existing `see D-NNN` is
  invalidated. The original conjoined text is in `b2f8cd5`. See **D-006**.
- 2026-09-14 · dantelyro — superseded by **D-023**. The entry assumed a document could be seeded
  from the same evidence as the rest of the set. It cannot: layout and stack are on disk, a `must`
  is not.
- 2026-10-14 · dantelyro — mvp removed by D-026; the Status line's claim that mvp owns the document and its format no longer holds.
