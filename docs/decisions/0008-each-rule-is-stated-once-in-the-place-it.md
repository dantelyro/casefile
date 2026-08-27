# D-008 — Each rule is stated once, in the place it applies

> **Reconstructed entry (2026-08-27).** Written from the body of `91ab5e1`, which records the
> counts and the reasoning contemporaneously.

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `91ab5e1`. This is a
`docs` commit rather than a `feat`/`fix`, taken because the rule it establishes governs no source
lines to blame; the commit body is the decision.
**Implemented by:** `91ab5e1` — 2026-08-27.

**Context:** The skills had accumulated the same rule in three or four forms at once: prose, a
negation of the prose, a red-flag bullet, and a "Rationalizations" row. `decisions/ is a sibling`
was stated three times in a single file. Every duplicate is a place the rule can be edited
without the others following.

**Options:** (a) leave it — repetition aids recall in a document the model reads under load;
(b) keep the tables as the canonical statement and thin the prose; (c) state each rule once, in
the section that owns it, and keep a red flag or rationalization row **only** where it carries
evidence the prose does not.

**Decision:** (c). Rationalizations went 13 → 6 rows, red flags 11 → 7, keeping only the rows
carrying their own evidence — vendor prose versus spec, mocks cannot verify a contract they
define, the 886-line log, the unsourceable name. Roughly 7,300 → 5,980 words with no rule
removed.

**Trade-offs:** A rule now appears once, so a reader who skims the wrong section misses it
entirely — the repetition was doing real work for a model reading under load. Accepted because
duplicated rules drift, and a skill that contradicts itself is worse than one that states a rule
once.

**The wider lesson, which outlives this entry:** this applies to the repo's own files as much as
to the skills it ships. `CLAUDE.md` points at `references/` rather than restating it.
