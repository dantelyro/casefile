# D-009 — The proposed doc set includes project instructions

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: stated directly when asking for the
change ("they should work together"). Not reconstructed.
**Implemented by:** `b2f8cd5` — 2026-08-27.

**Context:** `/init` and `evidence-based-decisions` only composed in one direction. Running
`/init` pulled in the skill, because the SessionStart hook had already fired. Invoking the skill
in a repo with no `CLAUDE.md` proposed an architecture document and a decision log and stopped
there — even though `references/living-documents.md` lists project instructions **first** in the
set, as the one document a session always loads.

The asymmetry produces a specific failure: a repo can end up with a decision log and no project
instructions, which means nothing points at the log. The skill cannot find it either — the hook
injects the trigger, not the location, and the location is per-project.

A second gap fell out of the same premise. The watermark was documented as living in the
architecture document's header, and a repo whose project instructions *are* its architecture had
nowhere to put one — as this repo demonstrated when its log was seeded.

**Options:** (a) leave it and rely on `/init` being run separately, accepting that a log created
by the skill alone is unreferenced; (b) have the skill write `CLAUDE.md` itself, duplicating
`/init`; (c) add project instructions to what the skill *proposes*, naming `/init` as what writes
them, and give the watermark a documented fallback location.

**Decision:** (c). The skill runs `/init` before creating anything else, and
`references/living-documents.md` gives the watermark a fallback location — the project
instructions header — for repos with no architecture document. The propose-then-ask contract is
unchanged.

**Trade-offs:** The skill now names `/init`, a Claude Code built-in, so it carries a dependency
on a harness feature that may not exist on every surface it runs on. Accepted because the
alternative — reimplementing project-instruction generation inside the skill — duplicates a
better-maintained thing and violates the same one-statement rule the skill preaches (D-008).

**The wider lesson, which outlives this entry:** a document is only as findable as the thing that
points at it. Creating half a set leaves the half you created unreachable.
