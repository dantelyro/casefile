# Remove `mvp` and `project-specs` — design

**Date:** 2026-10-14.
**Status:** Approved 2026-10-14.
**Release:** `0.12.0`. First of five; it clears the ground for `review` (0.13.0), `fix-bug` (0.14.0),
`implement` (0.15.0) and `write-specs` (0.16.0).

## Why

The developer's decision, 2026-10-14: neither skill was ever used on a real project, so nothing
depends on them, and the agent workflows replacing them were proven on Inverso instead. Removing them
first means no later release has to keep their triggers apart from the new skills'.

## What is removed

- `skills/mvp/` and `skills/project-specs/`, with all their references. Nothing is migrated.
- Their triggers (an idea to scope, `/init` in an empty directory, "scaffold this") are claimed by no
  skill afterwards. New-project setup becomes the first milestone of specs written by `write-specs`
  (0.16.0).

## What changes with them

- **`evidence-based-decisions` stops pointing at `mvp`**, or it would send work to a skill that no
  longer exists:
  - "No code, no docs → hand to `mvp`" becomes: no devflow skill writes specs yet, so say so and ask
    the developer. (`write-specs` takes this over in 0.16.0.)
  - "`docs/requirements.md` is never seeded here; `mvp` owns that document" (D-023) becomes: the
    evidence skill never seeds requirements or specs — code shows what a system does, never what it
    must do. No other skill owns `docs/requirements.md` any more.
- **`CLAUDE.md`**: the "four skills compose in one direction" and "`/init` on an empty directory
  belongs to `mvp`" sections and every mention of the removed skills are rewritten for the remaining
  two skills; the reconciliation watermark moves in the same commit.
- **`README.md`**: the skill list and any walkthrough of the removed skills.
- **`plugin.json` and `marketplace.json`**: the shared `description` no longer mentions turning an idea
  into a brief or building from generators. Both change together.
- **`docs/specs/2026-08-31-mvp-and-project-specs-design.md` and `docs/plans/2026-08-31-mvp-skill.md`**
  stay as history, each with a line at the top saying the skills were removed in 0.12.0 (D-026).
- **Version**: `0.12.0` (minor: the plugin's skill set changes).

## Decisions to record

- **D-026** — `mvp` and `project-specs` are removed. *Supersedes every entry that concerns only those
  skills*; each superseded entry's Status line says so, and entries that only partly concern them get a
  note instead. Which entries those are is decided by reading each of D-011 to D-025, not from their
  titles.

## Accepted when

- No file outside `docs/decisions/`, `docs/specs/` and `docs/plans/` mentions `mvp` or `project-specs`.
- `claude plugin validate --strict` passes on the repository.
- A fresh session in an empty directory with `/init` gets no devflow skill firing, and the evidence
  skill, triggered there, says no devflow skill writes specs yet instead of naming `mvp`.
