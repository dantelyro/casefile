# Client actors

## Why the client is a separate class

The client holds the business goal, and is the only actor in the cast with standing to say *"that
is phase two."* The dev team specifies everything, because specifying is what it is for. The domain
actors want everything, because none of them is paying for any of it. Without a client in the room
nothing is ever cut — and a skill named `mvp` that cuts nothing has failed at the one thing its
name promises.

What separates the class is **standing, not opinion**. A dev actor can say a feature is expensive
and a domain actor can say it is unnecessary; only the client can say the expense is not worth it
*this quarter*, and be right about it, because the quarter is the client's.

## The count is a property of the purpose

Never a fixed number, and never a quota to fill.

| Purpose shape | Clients | Why |
|---|---|---|
| Single audience, one buyer | 1 | There is no internal conflict to surface. A second client here is the first one paraphrased, and two agreeing voices read as corroboration when they are one voice twice |
| Two-sided — a marketplace, a platform | 2 | The side that wants listings free and the side that wants them curated are not one person. An MVP that serves only one of them is a finding, not a detail |
| Internal tool with a sponsor and users who did not ask for it | 2 | The sponsor's success criteria and the users' are routinely opposed, and the tool ships against the sponsor's. One client actor here always ends up being the sponsor |

The derivation, as a rule: **read `docs/purpose.md` for distinct parties whose success criteria
could conflict; one client per party; propose the count with the roster and say why that many.**

The reason for saying why is that the number is exactly the sort of thing that should be arguable
before a round is dispatched on it. Two clients who turn out to agree cost one round and establish
that the purpose has a single party in it — worth knowing. Two parties collapsed into one client
cost the conflict itself, and nobody finds out they had one.

## Why `docs/purpose.md` is drafted first

The client cast is derived from the purpose, so it cannot be assembled until the purpose exists in
writing. That dependency is why phase 2 precedes phase 3.

Three things are read out of `docs/purpose.md` when building the cast, and each maps to a slot in
the prompt below:

- **Who has the pain** — the parties, which set the count.
- **What done looks like** — each party's success criteria, which is what that client argues from.
- **The non-goals and the stated constraint** — budget, deadline, or the political reality, which
  is what gives the client something to cut *with*.

A purpose thin in any of the three produces a client actor with nothing to defend, and an actor
with nothing to defend agrees with the brief.

## The prompt template

One template, assembled per client. The substitution points are marked; everything else is fixed
wording and stays fixed, so that two clients differ in who they are and not in what they were
asked.

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

Two lines in there are doing more work than they look like they are.

**"You have never written software"** is what keeps the client from returning a specification. A
client actor that names a feature has skipped the step where the outcome was stated and could have
been met another way — usually a cheaper way, which is the whole point of having asked.

**The closing instruction** is what makes the claim tags possible downstream. The actor is the only
one who knows which of its sentences came from reading the brief and which it supplied from
nowhere; asked afterwards, it reconstructs, and a reconstruction is a guess with the same
confidence as the original. Sorting at the source is the only place the sort is cheap.

## Model note

**Client actors run on Sonnet, set on the `Agent` call at dispatch — never in frontmatter.**

Reference files carry no frontmatter to put it in, and `SKILL.md` is the wrong place for it: a
`model` there applies for the rest of the turn and not just while the skill runs, so it would
silently downgrade whatever the user opened the session to do (D-012 has the reasoning and the
trade-off). Per-dispatch, the override lives and dies inside the subagent.

Sonnet is enough because arguing a stated success criterion against a feature list is judgement
applied to two documents that are both in front of the actor. It is not the kind of work the dev
team is dispatched for.
