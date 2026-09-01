# D-020 — The seeding path splits by evidence grade

**Status:** Accepted (2026-08-31).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session.

**Implemented by:** `5dd1d3e` — 2026-08-31.

**Context:** `evidence-based-decisions` already seeds `docs/purpose.md` and `docs/requirements.md`
for a project with no doc set, reading them off the repo itself. `mvp` now seeds the same two files
from a cast of actors, when there is no code yet to read them off. The two skills were about to
claim the same empty directory, and a project with neither code nor docs would trigger both.

**Options:** (a) `mvp` takes all document seeding, including the case where code already exists;
(b) `evidence-based-decisions` keeps all of it, including seeding from an actor cast; (c) split the
path on whether code already exists.

**Decision:** (c). Seeding from a repo with code is Grade 1–2 evidence — layout, stack and entry
points on disk beat any actor's account of what the project probably is, so
`evidence-based-decisions` keeps that path unchanged. Seeding from a cast is unsourced by
construction: every line a `mvp` actor emits is `[reasoned]` or `[claimed — UNVERIFIED]`, tagged
because none of it is confirmed until a real person says so, which is a different evidence grade
requiring a different skill's handling — the tagging and quarantine discipline `mvp` already carries
and `evidence-based-decisions` does not. Handing the no-code case to `evidence-based-decisions`
would seed a project's foundational documents from the worse-evidenced source and lose that
discipline; handing the has-code case to `mvp` would ignore evidence already sitting on disk in
favor of dispatching a cast to guess at it.

**Trade-offs:** Two skills now describe seeding instead of one, and the boundary between them has
to be legible in both `description` fields or the wrong one fires on a given project. The two
descriptions are the only thing keeping the split from becoming two silently competing paths to the
same files.
