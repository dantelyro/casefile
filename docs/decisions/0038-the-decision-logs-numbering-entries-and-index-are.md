# D-038 — The decision log's numbering, entries and index are scripts

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: approved with the 0.16.0 spec (`docs/specs/2026-10-14-write-specs-design.md`) on 2026-10-14.
**Implemented by:** `6d433d5` — 2026-10-16 (the scripts), `2d69fbe` (the evidence skill uses them).

**Context:** The evidence skill numbered entries by `ls | tail -1`, wrote them by hand and kept the index by hand. Results varied with whoever did it: devflow's own index had dropped that D-022 also supersedes D-013. `write-specs` needs to write entries too.

**Options:** (a) each skill keeps doing it by hand from the reference; (b) `write-specs` restates the format; (c) three standard-library scripts in the evidence skill — the next id, a new entry, the generated index — run by both skills.

**Decision:** (c). The evidence skill owns the log and its format; `write-specs` runs `decision_new.py` and `decision_index.py` and links the format instead of restating it. The index is derived only from the entries' first and `Status` lines.

**Trade-offs:** Hand-written notes in the index are lost unless the entry's Status line carries them; `Supersedes D-NNN` is the one carried over.
