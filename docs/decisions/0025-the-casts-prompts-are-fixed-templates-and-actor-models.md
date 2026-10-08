# D-025 — The cast's prompts are fixed templates, and actor models are set per dispatch

> **Moved, not reconstructed.** The reasoning below was written alongside the `mvp` references in
> `ea6c78a`, `56b69f8`, `9c4d678` and `a1d6433` (2026-08-31) and lived in those files until
> 2026-10-08, when D-024's over-explaining rule moved maintainer-facing reasons out of the skills.
> The wording is carried over; only its location changed.

**Status:** Accepted (2026-08-31).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 2: blame on the implementing `feat`
commits above.
**Implemented by:** `ea6c78a`, `56b69f8`, `9c4d678`, `a1d6433` — 2026-08-31.

**Context:** `mvp` dispatches three actor classes (D-018) in parallel and blind (D-019). Each
dispatch needs a prompt and a model, and the purpose document they argue from has to exist before
the roster does.

**Options:** (a) free-form prompts written per run, inheriting the session model; (b) one fixed
template per class with marked substitution points, and a model chosen per class at dispatch.

**Decision:** (b), for these reasons, per element.

- **One template per class, not near-copies.** Five copies drift word by word until `security` is
  asked a subtly easier question than `backend`, and the difference between their answers stops
  meaning anything. Two clients must differ in who they are, not in what they were asked.
- **The dev team holds standing opinions.** A neutral reviewer arrives with fresh preferences each
  time, so the same idea run twice returns two different sets of objections, neither more right.
  Standing opinions make findings comparable across projects, and spare the actor relitigating
  decisions the repo already made. The three "none" cells in its table are written out so an empty
  cell is not read as an omission and filled in.
- **Load-bearing prompt lines.**
  - *"You have never written software"* (client) keeps the client from returning a specification;
    a named feature skips the step where the outcome could have been met a cheaper way.
  - *"Do not design it"* (dev team) — a returned design answers the open questions by quietly
    picking answers, which is the information the round exists to extract.
  - *"Speak only from your own experience"* (domain) — without it each actor answers for the whole
    domain, and three balanced surveys erase the divergence the cast exists to surface.
  - *"Do not be agreeable"* (domain) — asked to react to a proposal, a model finds the good in it.
  - *"Say what you actually do today and what you use to do it"* (domain) produces the incumbent,
    the thing the project has to beat, which is almost never in the brief.
  - *The closing instruction to mark world-assertions* (all classes) — only the actor knows which
    sentences came from the brief and which from nowhere, and only while writing; asked afterwards
    it reconstructs, with the same confidence as the original.
- **Models per dispatch, never in frontmatter.** A `model` key in `SKILL.md` names one model for
  the whole skill and applies for the rest of the turn (D-012), so it would collapse a mixed cast to
  one choice and silently downgrade whatever the user opened the session to do. Set on the `Agent`
  call, the override lives and dies inside the subagent. Clients and domain actors run on Sonnet:
  arguing a stated criterion against a feature list, or role-playing conditions, is judgement over
  documents in front of the actor. The dev team runs on the session model: its critique is the
  deliverable, and a finding never made cannot be recovered by a later phase.
- **`docs/purpose.md` is written twice.** Early, because the client cast is derived from it and a
  purpose written after the round only summarises the actors, so nothing in the round could have
  contradicted it. Late, because the round is what sharpens it.

**Trade-offs:** Fixed wording means a better prompt needs a deliberate edit to the template rather
than improvising per run. Sonnet actors are cheaper and may miss what the session model would
catch — accepted for roles whose input is two documents in front of them, refused for the dev team.
