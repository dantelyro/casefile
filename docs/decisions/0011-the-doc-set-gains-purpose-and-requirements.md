# D-011 — The doc set gains purpose and requirements

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: requested directly in session.
**Implemented by:** — pending; the change is in the working tree.

**Context:** The set covered how to run it, what exists, and why it is that way. It had nothing
for what the project is *for* or what it must do — so a decision entry could argue trade-offs
with no stated goal to trade against, and "done" had no definition to test against.

**Options:** (a) fold both into the architecture document; (b) two new members of the set.

**Decision:** (b). `docs/purpose.md` — the pain, who has it, and the non-goals, which is the half
that gets skipped and the only half that settles an argument. `docs/requirements.md` — functional
`F-NN` and non-functional `N-NN`, with stable ids so decisions and tests can cite them, and a
number on every non-functional one. Both sit above the architecture document in the seeding
order: architecture describes a shape that only makes sense once purpose and requirements are
settled.

**Trade-offs:** Five documents to keep true instead of three, and requirements rot faster than
anything else in the set. Mitigated only by the same non-overlap rule the others follow — purpose
holds no requirements, requirements hold no design.

**The wider lesson, which outlives this entry:** an unnumbered non-functional requirement cannot
be violated, only disappointed. "Fast" is not a requirement.
