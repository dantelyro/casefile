# D-022 — The cast replaces the scaffolder

**Status:** Accepted (2026-08-31).

**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session.

**Implemented by:** `a1933fe` — 2026-08-31.

**Context:** `scaffolding` created a project *and* owned the empty-directory trigger, so it decided
what to build at the same moment it decided how. The new `mvp` skill establishes what a project is
for and what it must do before anything is generated, which leaves `scaffolding` doing only the
second half of its old job.

**Options:** (a) keep `scaffolding` and let `mvp` feed it, two skills both claiming an empty
directory; (b) delete `scaffolding` and let the actors emit build commands directly; (c) rename it
to `project-specs`, narrow its trigger to "requirements exist, now build", and move `/init` to
`mvp`.

**Decision:** (c), by `git mv` so the 780 lines of references keep their history. (b) was refused
on D-015: `references/generators.md` carries a verification state on every command precisely
because a flag set written from memory is a hypothesis about a CLI. An actor emitting `nest new`
from memory is that exact failure, so the generator commands needed a skill to live in, not an
actor's recall.

**Trade-offs:** Two skills now exist where there was one, and the boundary between them has to be
legible in both `description` fields or the wrong one fires. A real residual is also left behind:
`references/questions.md` still asks its question set as though building from nothing, while
phase 1 of `project-specs` now reads `docs/requirements.md` first — auth and RBAC in particular
could already be settled there and get asked again here.
