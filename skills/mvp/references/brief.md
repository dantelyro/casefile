# The brief

Every actor in the cast — client, dev team, domain — receives exactly this text and nothing else.
There is no follow-up round where a vague answer gets clarified; the brief is written once, before
anyone reacts to it, and everyone reacts to the same copy. **The brief is the ceiling on output
quality.** A vague brief produces a vague cast, and no amount of dispatching afterward recovers
what was never asked.

Five questions, closed and ordered. Ask all five before writing anything — a later answer can
sharpen an earlier one, but none of them is optional.

## What is it

| Question | What it changes |
|---|---|
| What is it, in one sentence a stranger would understand? | The brief's first line. |

A sentence a stranger would understand rules out the pitch that only makes sense to someone who
already agrees with it. If the answer needs a second sentence to stop sounding like jargon, the
idea is not yet a sentence — it is still a feeling about a sentence.

## Who is it for

| Question | What it changes |
|---|---|
| Who is it for? Name the people, not a market segment. | The domain cast (`references/domain-actors.md`). |

"Small businesses" is a market segment; "the person who closes out the till at night" is a person.
The domain cast is derived from whoever gets named here, so a segment produces actors with nothing
to be wrong about — nobody closes out a market segment's till, so nobody can say the brief got it
wrong.

## What breaks without it

| Question | What it changes |
|---|---|
| What breaks, or stays painful, without it? | `docs/purpose.md`'s pain statement. |

This is the question that separates a product from a feature request. "It would be nice" describes
nothing that breaks; if nothing breaks and nothing stays painful, the project is optional, and an
optional project is the first thing a later phase cuts anyway.

## What does done look like

| Question | What it changes |
|---|---|
| What does done look like — how would you know it worked? | The client cast's success criteria. |

An answer in the form of a feeling ("people would be happier") is not checkable later. An answer in
the form of an observation ("the till closes out in under five minutes") is — and the client cast
argues from what's checkable, not from what's hoped for.

## What it is deliberately not

| Question | What it changes |
|---|---|
| What is it deliberately not? | `docs/purpose.md`'s non-goals, and the first thing cut. |

Naming a non-goal here means it was excluded on purpose, before a cast of actors had the chance to
want it. A scope that only shrinks in phase 7, under pressure, cuts whatever an actor argued
loudest for last — not necessarily the thing that mattered least.

## Writing the brief

The five answers become one paragraph, written to disk, and **shown to the user before anything
dispatches.** Not summarized back, not paraphrased in a status line — shown, in full, as the text
every actor is about to receive. An unreviewed brief is a guess that eight actors then spend a
round elaborating on; catching a wrong assumption here costs one read, catching it after round 1
costs the round.

## Not asked

Stack, framework, database, hosting, repo shape, component library — none of it. Those are build
parameters, not product questions, and they belong to `project-specs`, a skill that doesn't exist
yet. Asking them here invites deciding the build before deciding the product: a framework choice
made in the same breath as "who is it for" outlives the reasoning that produced it, and the next
person to read the brief inherits a decision with no argument attached.

Adding a question to this file is a decision. Record it.
