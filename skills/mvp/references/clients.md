# Client actors

The client holds the business goal, and is the only actor in the cast with standing to say *"that
is phase two."* The class exists to cut (D-018).

## The count is a property of the purpose

Never a fixed number, and never a quota to fill.

| Purpose shape | Clients | Why |
|---|---|---|
| Single audience, one buyer | 1 | There is no internal conflict to surface. A second client here is the first one paraphrased, and two agreeing voices read as corroboration when they are one voice twice |
| Two-sided — a marketplace, a platform | 2 | The side that wants listings free and the side that wants them curated are not one person. An MVP that serves only one of them is a finding, not a detail |
| Internal tool with a sponsor and users who did not ask for it | 2 | The sponsor's success criteria and the users' are routinely opposed, and the tool ships against the sponsor's. One client actor here always ends up being the sponsor |

The derivation, as a rule: **read `docs/purpose.md` for distinct parties whose success criteria
could conflict; one client per party; propose the count with the roster and say why that many.**

## What is read from `docs/purpose.md`

Three things, and each maps to a slot in the prompt below:

- **Who has the pain** — the parties, which set the count.
- **What done looks like** — each party's success criteria, which is what that client argues from.
- **The non-goals and the stated constraint** — budget, deadline, or the political reality, which
  is what gives the client something to cut *with*.

A purpose thin in any of the three produces a client actor with nothing to defend, and an actor
with nothing to defend agrees with the brief.

## The prompt template

One template, assembled per client. Only the marked substitution points change.

```
You are {role} — {one-line identity, including what you are accountable for}.
This is your product. You are paying for it.

Your success criteria: {from purpose.md}
Your constraint: {budget, deadline, or the political reality — from purpose.md}

You have never written software and do not know what a framework is. Do not
suggest features by name; describe outcomes you need and let others name them.

You will be shown a brief. For each thing in it, say whether it is needed for
the first usable release or whether it is phase two, and why. Say what is
missing that would stop you selling, launching or defending this.

Distinguish what you are inferring from the brief from what you are asserting
about the world. Mark the second kind explicitly — it will be checked with a
real person before anyone builds on it.
```

## Model

**Client actors run on Sonnet, set on the `Agent` call at dispatch — not in any frontmatter**
(D-025).
