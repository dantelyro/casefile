# D-001 — Skill content splits across two loading tiers

> **Reconstructed entry (2026-08-27).** The reasoning below is read from the README's "Layout"
> section and from `SKILL.md` structure — the author's own words about the split. Nothing here
> was stated by the author as a decision at the time. To be confirmed.

**Status:** Accepted (2026-08-06).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `a8831af`, the `feat`
commit that introduced `references/` alongside the first `SKILL.md`.
**Implemented by:** `a8831af` — 2026-08-06.

**Context:** A skill's `SKILL.md` is loaded in full every time the skill triggers, so its length
is a tax on every session that matches it. `evidence-based-decisions` carries material that is
long by nature: a decision-entry format, an attribution procedure, a probing procedure.

**Options:** (a) one `SKILL.md` holding everything, loaded whole on every trigger; (b) trim the
material down until it fits a small `SKILL.md`, losing the procedures; (c) keep `SKILL.md` to the
principles and move formats and procedures into `references/`, read only when the work needs
them.

**Decision:** (c). `SKILL.md` states the principles and points at `references/`; the reference
files are read on demand. `evidence-based-decisions` is 151 lines against 471 lines of references
— roughly a quarter of the material loads on a trigger.

**Trade-offs:** Two tiers means a placement judgement on every addition, and a rule can end up
stated in both — the failure `91ab5e1` later had to correct across the repo (see D-006). A reader
who wants the whole picture now makes several reads instead of one.

**The wider lesson, which outlives this entry:** the tier a document sits on is a cost decision,
not an organisational one. Ask what loads it and how often, before asking what it is about.
