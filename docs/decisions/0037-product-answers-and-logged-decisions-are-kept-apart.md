# D-037 — Product answers and logged decisions are kept apart, and nothing is accepted by silence

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: approved with the 0.16.0 spec (`docs/specs/history/2026-10-14-write-specs-design.md`) on 2026-10-14.
**Implemented by:** `9f4bb76` — 2026-10-16 (`write-specs`), `2d69fbe` (`Proposed` status).

**Context:** The pilot project kept `docs/specs/00-decisions.md`, one line each marked ✅, 🔵 or 🟡. Most lines were the owner's answers about the product ("Brazil first"), with no alternatives weighed and no evidence to grade; a few were real choices between alternatives. 🔵 meant "proposed by Claude, accepted unless changed", and read as decided.

**Options:** (a) one decisions file, as the pilot project's; (b) every answer as a decision entry; (c) answers as one-line product decisions in `docs/product/product-decisions.md`, real choices as entries in `docs/decisions/`, unanswered questions in `docs/product/open-questions.md`.

**Decision:** (c). `write-specs` sorts what an input produced into those three places, each with the spec rules it implies. Anything derived rather than said by the developer is shown as proposed at the one approval step; decision entries are written `Proposed` and become `Accepted` only on the developer's yes. A new status, `Proposed`, joins the log.

**Trade-offs:** Two places record what was settled, and a reader has to know which holds what. Splitting the pilot project's existing `00-decisions.md` is left for later, with the developer's agreement.
