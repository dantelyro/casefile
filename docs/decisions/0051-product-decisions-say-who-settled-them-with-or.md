# D-051 — Product decisions say who settled them, with ✅ or ❌

**Status:** Accepted (2026-10-21).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-21, answering 'Which icons' with option 1, then 'drop the bot icon', and 'Git user name' for the legend.

**Context:** product-decisions.md listed answers with no mark of who gave them, and write-specs let the developer's yes to a whole draft accept decisions Claude had inferred. inverso's docs/specs/00-decisions.md marks each line (✅ decided by the developer, 🔵 proposed by Claude, accepted unless changed, 🟡 open), which the developer asked for: 'i want icons like a tick and X or the thing not decided by me just like that one other repo'.

**Options:** (a) ✅ decided, 🤖 proposed by Claude, ❌ rejected; (b) inverso's ✅ and 🔵; (c) ✅ and ❌ only, with inferred decisions asked one by one; (d) plain lines, as before. For the legend's name: 'the developer', or git config user.name.

**Decision:** (c). Every line starts with ✅ (the developer decided it) or ❌ (the developer turned it down), under a legend '✅ decided by <name> · ❌ rejected by <name>' whose name comes from git config user.name. A decision write-specs inferred is asked as its own question; the yes to the draft never covers it (SPEC-006..008). The developer: 'oh yeah nothing is accepted by silence so drop the bot icon'; the legend's wording is a placeholder the developer will replace.

**Trade-offs:** Approval takes one question per inferred decision instead of one yes. A git user.name can name whoever owns the machine rather than whoever decided; it is written in the session where the developer approves, not reconstructed. spec_lint rejects existing product-decisions files without icons, so they need updating (D-052). (a) and (b) record a decision nobody explicitly made; (d) keeps that ambiguity.
