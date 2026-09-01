# Domain actors

## Two or three, chosen to disagree

The cast is small and it is selected for divergence. Take a site for hunters: a weekend bowhunter,
a commercial guide and a public-land elk hunter want three different applications. The guide wants
client bookings and liability paperwork; the weekend bowhunter wants to check a wind forecast from
a phone with one bar; the elk hunter wants public-land boundaries that are correct, and does not
care about either of the other two.

That spread is the output. **Where they agree, you have a candidate core requirement** — three
people with opposed interests wanting the same thing is the strongest signal a round of this shape
can produce. **Where they diverge, you have scope**: something to cut, defer, or make
configurable, and now you know who loses under each choice.

So a cast that agrees with itself has been chosen badly, not confirmed. If the three proposed
actors would answer every question the same way, they are one actor described three times, and the
roster should be reworked before dispatch rather than after the answers come back identical.

Two or three, because one cannot disagree and four is mostly the third one again with a different
region attached.

## Distinct from the client

The client owns the product; the domain actors live in the world it is for. Nobody in this class
is paying for anything, and nobody in this class has to sell it.

**Their conflict is the most useful thing this skill produces.** The client wants the feature that
closes a sale; the domain actor wants the one that works with cold hands at 5am. Both are real
requirements, they are not the same requirement, and a project that hears only the first ships
something that demos well and is abandoned in the field. Keep the two positions separate through
synthesis — merging them into a single "user need" deletes exactly the tension worth carrying into
the cut.

## Specificity is the whole value

"A hunter" produces a Wikipedia summary. "Fifteen years bowhunting whitetail on public land in
central Pennsylvania, weekends only, day job" produces detail you can act on — because the second
description has conditions in it that the brief can contradict, and the first does not.

Derive four things from the brief for each actor:

| | What it fixes |
|---|---|
| Discipline | What they actually do, as opposed to the category they belong to |
| Region | Rules, seasons, terrain, infrastructure — most of what makes an assumption wrong is local |
| Frequency | Daily practice and occasional practice are different jobs with different tolerances |
| Constraint | Time, money, connectivity, a body that is fifty-five years old — the thing that makes a feature unusable rather than merely unloved |

Where the brief does not say — and a brief that answered its "who is it for" question with a market
segment will not say — **that gap is itself a finding**, and it belongs in the roster proposal.
Inventing a region to fill the slot buries the fact that nobody has decided where this thing is
for.

## Everything they say is invented

A domain actor has never hunted, never closed out a till, never filed the paperwork. It is a
language model doing an impression of someone who has, and the impression is fluent in exactly
the places it is least reliable — prices, regulations, local rules, what the incumbent tool costs.

So the standing rule for this class: **its assertions about the world route to
`[claimed — UNVERIFIED]`.** The exception is narrow, not generous — a domain actor reasoning about
the *brief* ("your description assumes I have signal, and it says I am in a national forest") is
reasoning from a document that is in front of it, and is tagged accordingly.

This does not make the class less worth dispatching. An invented objection still points at a
question nobody had asked, and a question is a cheap thing to take to a real person. What is
expensive is an invented answer that reached the requirement list without the tag.

## The prompt template

```
You are {name}, {age}, {specific identity: discipline, region, frequency,
constraint}. {One line on what your days actually look like.}

You have never built software and do not care how it works.

You will be described something someone wants to build for people like you.
Say what you actually do today and what you use to do it. Say what about the
description would not survive contact with your real conditions. Do not be
agreeable — if it would not help you, say so plainly.

Speak only from your own experience. Do not speak for other kinds of {domain}
whose situation you do not share.
```

**That last line is load-bearing.** Without it a single actor answers on behalf of the whole
domain — "well, some hunters would want X, though others prefer Y" — and every actor returns the
same balanced survey. The divergence the cast exists to surface disappears, and it disappears
quietly, into three answers that all look reasonable.

**"Do not be agreeable"** is the second load-bearing line, for the same structural reason: asked to
react to a proposal, a model will find the good in it. A domain actor that likes everything has
confirmed the brief without testing it.

**"Say what you actually do today and what you use to do it"** earns its place by producing the
incumbent. What someone already uses — a notebook, a spreadsheet, a rival app, nothing at all — is
the thing the project has to beat, and it is almost never in the brief.

## Model note

**Domain actors run on Sonnet, set on the `Agent` call at dispatch, never in frontmatter** — see
the reasoning in `clients.md`, which applies here unchanged.

Role-play is cheaper work than architectural critique. The actor is describing conditions and
reacting to a paragraph, not tracing consequences through a system that does not exist yet.
