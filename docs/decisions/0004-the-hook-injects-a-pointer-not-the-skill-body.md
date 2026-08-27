# D-004 — The hook injects a pointer, not the skill body

> **Reconstructed entry (2026-08-27).** Read from the author's comment in `hooks/session-start`
> and the matching README paragraph, both written with the change. The "few hundred tokens"
> figure is the author's; it has not been measured for this entry.

**Status:** Accepted (2026-08-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `2a2476b`, the `feat`
commit that added `hooks/session-start`.
**Implemented by:** `2a2476b` — 2026-08-19.

**Context:** Given D-003, the hook has to put *something* in front of the model at session start.
A `SessionStart` hook can emit arbitrary text, so the whole of `SKILL.md` is available to it.

**Options:** (a) inject the skill body, guaranteeing the model has the content whether or not it
invokes the tool; (b) inject a short directive naming the skill and let the `Skill` tool load the
content on demand.

**Decision:** (b). The directive is a few hundred tokens; `SKILL.md` plus its references is
several thousand, and would be paid by every session regardless of whether the skill turned out
to apply.

**Trade-offs:** The load now depends on the model actually invoking the tool. An injected body
cannot be ignored; a pointer can. Accepted because the alternative taxes every session in every
project to remove a failure mode in some of them — and because injecting the body would make
D-001's two-tier split pointless for this skill.

**The wider lesson, which outlives this entry:** injected context is paid unconditionally, tool
loads are paid on demand. Prefer the pointer whenever the content is conditionally useful.
