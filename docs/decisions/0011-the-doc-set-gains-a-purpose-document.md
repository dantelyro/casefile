# D-011 — The doc set gains a purpose document

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: requested directly in session.
**Implemented by:** `b2f8cd5` — 2026-08-27.

**Context:** The set covered how to run it, what exists, and why it is that way. It had nothing for
what the project is *for* — so a decision entry could argue trade-offs with no stated goal to trade
against.

**Options:** (a) fold it into the architecture document; (b) a new member of the set.

**Decision:** (b). `docs/purpose.md` — the pain, who has it, and the non-goals, which is the half
that gets skipped and the only half that settles an argument. It sits above the architecture
document in the seeding order: architecture describes a shape that only makes sense once the
purpose is settled.

**Trade-offs:** One more document to keep true, held to the same non-overlap rule as the rest of the
set — purpose holds no requirements, and no design.

**Changed by:**
- 2026-09-14 · dantelyro — split in two. This entry originally decided two documents at once, under
  the title "The doc set gains purpose and requirements", and was renamed from
  `0011-the-doc-set-gains-purpose-and-requirements.md`. The requirements half moved to **D-011b**
  so it could be superseded on its own; the purpose decision is unchanged in substance. The
  original conjoined text is in `b2f8cd5`. See **D-006**.
