# D-019 — Parallel dispatch over a round table

**Status:** **SUPERSEDED by D-026 (2026-10-14).** mvp, whose cast this entry dispatches, is removed. Accepted (2026-08-31).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session.

**Implemented by:** `4a28363` — 2026-08-31.

**Context:** The cast's answers have to be gathered somehow, and a round table — every actor in one
shared thread, seeing each other's positions as they form — is the obvious mechanism. It is also
the one to record as rejected on purpose, because **a round table produces better-sounding
answers**, and the reasoning that turned that down is exactly the kind that gets lost and then
re-litigated by whoever next reaches for the obvious mechanism.

**Options:** (a) a round table — one shared thread, all actors present, discussing to consensus;
(b) parallel dispatch only — every actor answers blind, nothing after round 1; (c) parallel dispatch
with a second, targeted round — actors are shown a contradiction only, only if one exists, only the
actors in it.

**Decision:** (c). (a) was rejected: actors in a shared thread converge socially rather than on the
merits — an objection gets dropped after one push-back, and the transcript that results cannot
distinguish a conceded argument from an agreeable model, because both look identical on the page.
For a skill whose deliverable is *unresolved disagreement made visible* — the requirements file's
`Cut` section exists to keep a losing argument attributable — a mechanism that manufactures
agreement attacks the product directly, not incidentally. A second, independent reason: the
orchestration a round table needs (turn-taking, who speaks next, when to stop) is hand-rolled and
would be the single most breakable part of the skill, for a payoff that is mostly the appearance of
deliberation. (b) was rejected too, in the other direction: round 1 alone leaves every contradiction
sitting unresolved with no attempt made, which throws away cheap information a targeted second pass
recovers at the cost of one more dispatch, only when there is something to dispatch it for.

**Trade-offs:** Blind actors find gaps in the brief only. A gap that exists only once one actor has
proposed something — the kind another actor would catch instantly on seeing that proposal, and
cannot catch otherwise because in round 1 the proposal does not exist yet — is missed. Round 2
recovers some of these, but only along the lines synthesis already spotted a contradiction to
chase; it cannot surface an interaction nobody collided over. That is the accepted cost of not
running a round table, taken deliberately in exchange for the independence that makes round 1 worth
reading at all.

**Changed by:**
- 2026-10-14 · dantelyro — superseded by D-026; mvp removed.
