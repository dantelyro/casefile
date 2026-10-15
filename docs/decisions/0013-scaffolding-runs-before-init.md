# D-013 — Scaffolding runs before `/init`

**Status:** **SUPERSEDED by D-022 (2026-08-31).** `scaffolding`, the skill this entry names, no
longer owns the empty-directory trigger — it was renamed to `project-specs` and narrowed to build
from documents that already exist. The `/init`-in-an-empty-directory trigger moved to `mvp`. D-022
is itself superseded by D-026 (2026-10-14): `mvp` is removed and no skill claims `/init` in an empty
directory.
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: requested directly in session ("this
skill will trigger on /init too but will run before init since init will have nothing to do").

**Implemented by:** `19d9e44` — 2026-08-30.

**Context:** `/init` writes project instructions by reading the codebase. `evidence-based-decisions`
already claims `/init` as a trigger, and its own guidance is to run `/init` *first*, before the rest
of the doc set (D-009). In an empty directory both of those are vacuous: there is no code to read
and nothing to describe.

**Options:** (a) leave `/init` to `evidence-based-decisions` and have the user invoke scaffolding by
name; (b) claim `/init` in the scaffolding skill's `description` and state the precedence there;
(c) state the precedence in both skills so whichever fires knows about the other.

**Decision:** (b). The precedence lives in one place — `skills/scaffolding/SKILL.md` — and
`evidence-based-decisions` is not modified.

**Trade-offs:** Both descriptions now match a bare `/init`, and which skill fires is the model's
judgement rather than a routing rule. The disambiguator is the state of the directory, which is
cheap to check and stated in scaffolding's description ("a directory that holds no project yet").
(c) would make that judgement more reliable at the cost of the same rule living in two files that
can disagree — exactly what D-008 forbids. If the wrong skill turns out to fire in practice, the fix
is sharpening scaffolding's `description`, not duplicating the rule.

**Unverified:** no observation of which skill actually fires on `/init` in an empty directory. This
is a design intent, not a measured behaviour.

**Changed by:**
- 2026-08-31 · dantelyro — superseded by D-022; the reasoning that an empty directory has nothing
  to document still holds, but the skill named here no longer exists under that name and no longer
  claims the trigger. See D-022 for the split between `mvp` (owns `/init` on an empty directory)
  and `project-specs` (builds from documents `mvp` produces).
- 2026-10-14 · dantelyro — D-022 superseded by D-026; the /init trigger no longer belongs to any skill.
