# D-026 — `mvp` and `project-specs` are removed

**Status:** Accepted (2026-10-14). Supersedes D-014, D-015, D-017, D-018, D-019, D-021, D-022, D-025.
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session ("you may drop mvp and
project-specs completly cause i never tested them").
**Implemented by:** this change.

**Context:** devflow is gaining agent workflows (`review`, `fix-bug`, `implement`, `write-specs`,
designed in `docs/specs/2026-10-14-*`), generalised from the workflow that built Inverso M0–M1. That
workflow starts from specs with rule IDs written after a free brainstorm, not from a cast of actors,
and it builds a project as its first milestone rather than through a separate scaffolding skill.
`mvp` and `project-specs` were never used on a real project.

**Options:** (a) keep both beside the new skills and keep their triggers apart; (b) fold their content
into the new skills; (c) remove both, migrating nothing.

**Decision:** (c), as the first release (0.12.0), before any new skill lands. `skills/mvp/` and
`skills/project-specs/` are deleted with their references. Their design and plan documents stay as
history, marked as such. Entries that existed only for these skills are superseded; entries that still
govern something get a `Changed by` note instead (D-016, D-020, D-023, D-024), and D-011b and D-013 have
their status lines corrected.

What carries over, and where:

- **No hand-typed package versions** (the developer's rule behind D-015 and D-017: "always run npm
  command as much as possible") — passes to the implementer agent in 0.14.0: dependencies are added with
  the package manager's command, never by writing a version into a manifest.
- **No dependency on another plugin's files** (D-016, "ruled out independently and permanently") —
  stays in force; D-016 is kept Accepted with a note for that reason.
- **The evidence skill's no-code branch** used to hand to `mvp`. It now says no devflow skill writes a
  new project's specs yet and asks the developer; `write-specs` (0.16.0) takes it over.

**Trade-offs:**

- `docs/requirements.md` has no owner. D-023 already accepted that the evidence skill never seeds or
  reconciles it, on the basis that `mvp` at least produced it with quarantine tags; now nothing
  produces it. Projects specced with `write-specs` use `docs/specs/` instead.
- `docs/discovery/` is dropped from the evidence skill's doc set: its only producer was `mvp`'s cut.
  Decisions a brainstorm makes go to `docs/decisions/` through `write-specs`.
- The tagging discipline for unsourced claims (`[claimed — UNVERIFIED]`) and D-011b's lesson that an
  unnumbered requirement "cannot be violated, only disappointed" survive only in superseded entries.
  `write-specs` keeps the second through rule IDs and `[VERIFY]`.
- Until `write-specs` ships, no devflow skill claims `/init` in an empty directory.
