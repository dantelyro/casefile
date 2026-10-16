# D-032 — Instructions used by more than one skill live in `shared/`

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: proposed in session on 2026-10-14 when the
merge procedure needed a home both `fix-bug` and `implement` could use, and approved with the 0.14.0
spec the same day.
**Implemented by:** `e2e4113` — 2026-10-15.

**Context:** `fix-bug` (0.14.0) and `implement` (0.15.0) merge the same way. A skill's long material
lives in its own `references/` (D-001), and a reference must be linked directly from `SKILL.md`, never
through another reference (D-024).

**Options:** (a) the procedure in `fix-bug/references/`, with `implement` reaching into another skill's
folder; (b) a copy in each skill; (c) a top-level `shared/` folder, each skill linking the file
directly from its `SKILL.md` as `${CLAUDE_PLUGIN_ROOT}/shared/<file>.md`.

**Decision:** (c). No skill owns another's procedure, there is one copy (D-008), and the link is one
level deep from every `SKILL.md` that uses it, so D-024 holds.

**Trade-offs:** A file in `shared/` belongs to no skill, so a change to it changes every skill that
links it; whoever edits it checks each. `${CLAUDE_PLUGIN_ROOT}` is substituted only in plugin skills, so
the arrangement depends on devflow staying a plugin.
