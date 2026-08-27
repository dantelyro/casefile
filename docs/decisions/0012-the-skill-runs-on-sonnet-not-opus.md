# D-012 — The skill runs on Sonnet, not Opus

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: requested directly in session
("i dont think that skill needs opus so a cheaper model should be enough").

**Implemented by:** `d366ff9` — 2026-08-27.

**Context:** `evidence-based-decisions` fires on every session start via the hook (D-003). Its
work is mechanical: read a watermark, replay a commit range, read the diffs, update what they
invalidated. That is comprehension and bookkeeping, not the reasoning Opus is priced for.

Evidence for the mechanism, Grade 3 — the Claude Code skills reference, not observed behaviour:
`model` is a supported `SKILL.md` frontmatter field, taking the same values as `/model` plus
`inherit`.

**Options:** (a) leave it inheriting the session model; (b) `model: sonnet`; (c) `context: fork`
plus `model: sonnet`, running the skill in its own subagent.

**Decision:** (b), as asked.

**Trade-offs:** Per the same reference, a skill's `model` override **applies for the rest of the
turn**, not just while the skill runs. Because the hook fires the skill at session start, the
user's entire first turn now runs on Sonnet — including whatever they actually opened the session
to do. (c) avoids this by confining the override to a forked subagent, at the cost of the skill
losing the main conversation's context and having to hand back a report rather than ask a
question directly — which the propose-then-ask contract (D-009) depends on.

**Open question, deliberately not decided here:** whether the turn-wide downgrade is acceptable
in practice, or whether the fork is worth losing direct propose-then-ask for. Unverified either
way — this has not been observed, only read.
