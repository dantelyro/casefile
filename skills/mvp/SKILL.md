---
name: mvp
description: >
  Use when an idea for a new project needs to become something buildable — deciding what is worth
  building first, what the project is for, and what it must do. Triggers on: "what should I build
  first", "what am I missing", a feature list nobody has challenged, an idea about to be scoped, a
  project with no `docs/requirements.md`, or a brief that needs cutting to a defensible MVP. Not
  for adding a feature to a project whose requirements already exist.
---

# MVP

## Overview

An idea usually arrives as a feature list, and the list is the problem. It holds what one person
thought of in one sitting, in the order they thought of it, with nothing marked optional and
nobody named as wanting any of it. Built in that shape, the project discovers its missing half
after the first release and its unnecessary half after the second.

**Core principle: dispatch a cast, then cut.** A client, a dev team and people who live in the
domain are given the idea separately and asked what they need from it. The output is the smallest
thing that still serves the purpose, plus the record of what was cut and who wanted it — a cut
with an advocate attached can be reopened later, an anonymous one is just an absence.

## The three actor classes

| Class | Where they come from | What they answer |
|---|---|---|
| Client | `docs/purpose.md` — the count follows the purpose, never a quota | Who is this for, and what makes it worth paying for |
| Dev team | A fixed five, identical every run | What breaks, what it costs, what must exist before anything ships |
| Domain | The brief — the world the project is going to live in | What actually happens out there, and what the brief assumes wrongly |

Their prompts live in `references/clients.md`, `references/dev-team.md` and
`references/domain-actors.md`, and are not restated here. A prompt kept in two places drifts, and
then the roster you dispatch is not the roster you documented.

## Two claim types

Every line an actor emits carries one of two tags. This section is what the rest of the skill
rests on: untagged, a fabricated fact and a traceable inference read exactly alike.

- **`[reasoned]`** — an inference from the brief, from `docs/purpose.md`, or from another actor's
  stated position. The reasoning travels with the claim, so it is verified by reading it.
- **`[claimed — UNVERIFIED]`** — an assertion about the world outside your documents: a
  regulation, a price, a competitor, how a job is really done. Grade 4 on the evidence ladder in
  `evidence-based-decisions`, because an actor is a language model and a confident sentence about
  the world costs it nothing. Quarantine it, never merge it into the requirement list, and confirm
  it with a real person before anything is designed around it.

**The tag goes on the claim, not the actor.** One client actor emits both kinds in a single
paragraph — *"I need X, because the purpose says Y"* beside *"regulators require Z"* — so tagging
by speaker discards the distinction the tags exist to draw.

## Seven phases

1. **Write the brief.** The idea as one document, before anyone reacts to it, so every actor
   reacts to the same thing. `references/brief.md`
2. **Draft `docs/purpose.md`.** What the project is for. The roster is derived from it, which is
   why it cannot wait until after.
3. **Propose the roster and wait.** Names, classes, counts, and the reason for each. A stop.
4. **Round 1 — parallel and blind.** Each actor answers without seeing another's answer. Shared
   context makes them converge, and convergence reads as agreement.
   `references/clients.md` · `references/dev-team.md` · `references/domain-actors.md`
5. **Synthesize.** Group the answers, surface the conflicts, keep them intact. `references/synthesis.md`
6. **Round 2 — targeted.** Put each conflict back to the actors who caused it. `references/synthesis.md`
7. **Cut to an MVP**, refine `docs/purpose.md`, write the documents. `references/documents.md`

## Nothing is written unasked

The skill offers `docs/purpose.md` and `docs/requirements.md` and waits for an answer. No devflow
skill creates a document in a project that has not agreed to it: an unwanted file is one more
thing that has to be kept true, and it will not be kept true.

## Red flags — stop

- A `[claimed — UNVERIFIED]` line promoted into the requirement list with no human confirming it
- A roster dispatched before it was approved
- An MVP with nothing cut from it — nothing was cut, so nothing was decided
- A requirement with no actor attributed to it
- `docs/purpose.md` written after the roster instead of before it
- Actors handed each other's answers in round 1

## Rationalizations

| Excuse | Reality |
|---|---|
| "The actors all agreed, so it must be true" | They share one model and one brief. Agreement among fabrications is not evidence of anything; a round that produced no conflict produced no information. |
| "I'll attribute the requirements later" | By then the advocate is gone and the line reads as fact. Attribution is what makes a requirement arguable instead of inherited. |
| "The client actor is basically the user" | The client owns the product; the domain actor lives in the world it is for. Their conflict is the most useful thing this skill produces, and merging them deletes it. |
| "This one is obviously true, it doesn't need a tag" | Obvious is how a Grade 4 claim gets into the requirement list. The tag costs a word. |
| "The list is already small, there is nothing to cut" | Then say what was considered and rejected. An MVP with no cuts recorded is an unexamined feature list with a new name. |

## References

| File | Read when |
|---|---|
| `references/brief.md` | Phase 1 — what the brief must contain before anyone reacts to it |
| `references/clients.md` | Phase 3–4 — deriving client actors from the purpose, and their prompt |
| `references/dev-team.md` | Phase 3–4 — the fixed five and what each one is asked |
| `references/domain-actors.md` | Phase 3–4 — deriving domain actors from the brief, and their prompt |
| `references/synthesis.md` | Phases 5–6 — grouping, conflict handling, the round 2 questions |
| `references/documents.md` | Phase 7 — the cut, and the format of `purpose.md` and `requirements.md` |
