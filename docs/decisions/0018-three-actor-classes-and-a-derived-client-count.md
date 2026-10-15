# D-018 — Three actor classes, and a derived client count

**Status:** **SUPERSEDED by D-026 (2026-10-14).** mvp, whose cast this entry shapes, is removed. Accepted (2026-08-31).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session.

**Implemented by:** `33de657` — 2026-08-31.

**Context:** `mvp` dispatches a cast at an idea before anything is built, and the cast's shape
decides what the skill can find. A dev team alone specifies everything it is handed and cuts
nothing, because specifying is what it is for. Domain actors want everything, because none of
them is paying for any of it. Neither has standing to say "that is phase two" — and a skill named
`mvp` that cuts nothing has failed at the one thing its name promises.

**Options:** (a) one undifferentiated cast, everyone answering the same prompt; (b) a dev team
plus domain actors, no client; (c) three classes — client, dev team, domain — with the client
count derived from `docs/purpose.md` rather than fixed.

**Decision:** (c). The client class exists because it is the only one with the standing to cut,
and its size is read out of the purpose rather than chosen: one client per party whose success
criteria could conflict, per `references/clients.md`. A single-audience purpose gets one client; a
two-sided purpose gets two, because the side that wants listings free and the side that wants them
curated are not one person, and collapsing them into one voice deletes the conflict before it can
be surfaced. A fixed count would either force a second client to paraphrase the first or force one
client to speak for two opposed parties — both quieter failures than getting the number wrong out
loud, in a proposal step that stops for approval before any round is dispatched.

**Trade-offs:** A class whose size is computed rather than fixed is one more thing the roster
proposal has to justify — a fixed dev team of five needs no argument for its count, and derived
client count needs one every run. Getting the derivation wrong is invisible at proposal time: a
purpose that is actually two-sided but reads as one produces a plausible single-client roster, and
the gap does not surface as an error, it surfaces as an MVP that serves one side of a two-sided
product and ships anyway.

**Changed by:**
- 2026-10-14 · dantelyro — superseded by D-026; mvp removed.
