# D-075 — casefile drops its specs, plans, build order and evals, built and unbuilt alike; new milestones start fresh

**Status:** Accepted (2026-11-01).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-01, in the developer's words quoted below

**Context:** After M12 (PR #1, 0.29.0), the developer deleted docs/specs (its history designs included), docs/plans, docs/product/blueprint.md and evals/. A review the same day found the plugin unaffected (288 tests pass, claude plugin validate passes; no code reads those files) but left dangling: 54 citations of casefile's own rule IDs and decisions in skill, reference and agent text Claude loads at runtime, references in CLAUDE.md and the README, rule arrows in product-decisions.md, and issue 0001's reproduction, which uses docs/plans/M1.md. Restoring was possible from git; remaking specs from the code was possible too, but write-specs never reuses an ID, so remade rules could not reconnect to the old citations.

**Options:** (a) restore the deleted files and trim only what is unwanted; (b) remake specs for the built behaviour from the code, under new IDs; (c) keep them deleted, drop the unbuilt plans with them, and specify only new milestones from here on.

**Decision:** (c), the developer's call: 'milestone where already a mess so from here on out i will make new ones', and of the unbuilt work: 'what was not built i would drop cause it was already a mess'. The planned code-practices skill and Stop-hook lint (M9, M10: PRAC-001 to 012) and the refactor milestone's open questions (M8) are dropped with the rest. Built behaviour stays protected by its tests, and the decision log stays.

**Trade-offs:** The [MANUAL] rules, about 28 of the last 50, were the only checklist of skill and reviewer behaviour no test covers; it is gone. spec_lint and rules_coverage cannot run on casefile until new specs exist. Old rule IDs cited in skill text, hook comments and test names point at nothing until they are stripped, and are never reused. The designs of 0.12 to 0.16 survive only in git. The code-practices work, the question this session began with, has to be specified again from nothing.
