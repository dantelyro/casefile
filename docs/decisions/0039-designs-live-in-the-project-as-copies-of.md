# D-039 — Designs live in the project as copies of their artifacts

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: approved with the 0.16.0 spec (`docs/specs/2026-10-14-write-specs-design.md`) on 2026-10-14.
**Implemented by:** `9f4bb76` — 2026-10-16 (`write-specs`).

**Context:** The pilot project's design system and screens were made as claude.ai artifacts. A link can change or disappear without the project noticing, and the design check and the implementer read files, not links.

**Options:** (a) specs link to the artifacts; (b) the project keeps a copy of each, under `docs/product/design-system/` and `docs/product/design/`, and the copy is the source of truth.

**Decision:** (b). The developer names the artifact; `write-specs` finds it among those the account can open, and copies it after the approval step. A name with several matches, or an artifact shared from another organisation, needs the link.

**Trade-offs:** Copies drift from the artifact if someone edits the artifact and not the project; the project's copy wins.
