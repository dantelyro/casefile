# D-052 — devflow keeps its documents in its current format, with no docs skill

**Status:** Accepted (2026-10-21).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-21, in the developer's words quoted under Context, then option 'Points 1–8' and 'yes write it and build it'.

**Context:** M5 planned a separate skill (DOCS-001..008) to move a project's documents into write-specs' layout, after the 2026-10-19 product decision that documents are brought into the layout by a separate skill. D-050 already has the evidence skill replace a mental-model.md with an overview without asking. The developer: 'devflow will always enforce his own documents structure so old doc can be updated to the new format. drop the recolicialion skill its actually uneeded'.

**Options:** (a) build the M5 docs skill; (b) session_start names documents in an older format and the evidence skill rewrites them, for mental-model.md and product-decisions.md; (c) the same for every document devflow defines.

**Decision:** (b). session_start names a mental-model.md, or a product-decisions.md without its legend or icons (EVID-004); the evidence skill rewrites them in the current format without asking, in one commit, asking only for a fact the record cannot show, such as who decided a product decision (EVID-005, critical). The docs skill and DOCS-001..008 are removed, and the 2026-10-19 product decision is marked rejected.

**Trade-offs:** Moving a project's arbitrary old documents into the layout (DOCS-003/004: misread specs, git mv with link rewrites) has no skill now. (c) was proposed and set aside by the developer as 'too extreme for now'. Rewriting without asking can change a file the developer edited by hand; git history keeps it.
