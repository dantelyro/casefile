# Synthesis and the second round

Round 1 returns one answer per actor, written blind. Synthesis is a **read across** them, not a
merge into them. Merging is the tempting move — the answers overlap, and a single deduplicated list
is shorter than one document per actor — but the overlaps and the collisions are the only new
information the round produced. A merged list has thrown both away and kept the prose.

So the output of this phase is not a list of requirements. It is three groups, and phase 7 of the
skill turns them into one.

## What synthesis is looking for

**1. Contradictions — two actors whose positions cannot both be built.**

The worked example the cast produces on its own: `frontend` argues for offline writes, because the
screen it is designing has no connection and the entry still has to be recorded; `backend` argues
for a server-authoritative record, because two copies of the truth that both accepted a write have
to be reconciled by someone and no one has said who. Neither actor is wrong. They were never asked
the same question — one was asked what the user is looking at, the other what is true afterwards —
and the disagreement only exists once their answers are laid side by side.

That is the shape to hunt for: not an actor being mistaken, but two correct answers to two
questions that turn out to be one question.

**2. Undecided questions — something no actor could answer from the brief.**

Where every actor either skipped a point or guessed differently at it, the brief did not decide it.
These are **`docs/purpose.md` gaps, not requirements.** A requirement asserts what the thing must
do; an undecided question has nobody yet who wants anything. Writing one into the requirement list
as a line item invents an answer and hides the fact that it was invented — the same failure the
brief's "who is it for" question guards against upstream.

**3. Single-source claims — asserted by exactly one actor.**

Weak by construction. One voice is one voice whether or not it sounds certain, and nothing in a
blind round corroborates it. Note the source and carry it forward tagged; do not delete it, because
a single source is still a question worth asking a real person.

The standing example is a commercial operator's business model arriving as a user need: the guide
actor wants client billing, says so in the register of something the domain requires, and no other
actor in the cast mentions it. It is not a lie — it is what he needs — but it is one party's
economics wearing the clothes of a shared requirement, and only the "exactly one source" test
catches that while it is still cheap.

## Tagging goes on the claim, not the actor

`SKILL.md` states the rule and what each tag means. What this phase adds is the **test you apply
with the round-1 text in front of you**:

> Does this follow from a document we have, or assert something about the world we do not?

One actor emits both kinds, often in one paragraph. A client saying *"your purpose says weekend
hunters, this feature only serves guides"* is `[reasoned]` — the purpose is on disk and the
inference is checkable by reading it. The same client saying *"nobody pays more than ten a month
for this"* is `[claimed — UNVERIFIED]` — there is no document behind it, and the actor's confidence
is not evidence of one.

Applying the test per claim rather than per speaker is what keeps the second sentence from
inheriting the first sentence's credibility.

## When round 2 is worth dispatching

**Only for a contradiction, only the actors in it, each shown the other's position.** Nothing else
earns a second dispatch:

- **Not for undecided questions.** Nobody has the answer; that is what made it undecided. Asking
  again produces an answer, which is worse than the gap it filled.
- **Not for single-source claims.** A second pass makes an invention more fluent, not more true.
  The only thing that resolves one is a person outside the cast.

If round 1 produced no contradictions, round 2 does not run and **that costs nothing.** A coherent
brief genuinely has less to fight about, and a phase that skips itself when there is nothing to do
is the design working rather than failing. Manufacturing a conflict to justify the round produces a
conflict that was never real and then resolves it, which reads in the record exactly like a real
finding.

## Resolve or hold

A re-dispatched actor is shown the other position and must return **one of two shapes**:

- *"I concede X, because Y."*
- *"I still hold X, because Y."*

The reason is the required part in both. A concession with no reason is noise — an actor agreeing
under the social pressure of having been contradicted, which is the failure mode of asking a model
to reconsider anything. Record it as unresolved, not as agreement.

**An unresolved contradiction is a finding, not a failure.** It goes into the session record as an
open decision with both positions intact and both reasons attached. Two specialists holding
opposite positions for stated reasons is the most honest input a cut can have — it names a choice
that has to be made by a person, and hands them the argument already assembled instead of making
them reconstruct it.

## The limitation, stated so it is not rediscovered as a bug

Blind actors find gaps **in the brief** only.

A gap that exists only once `backend` has proposed permission inheritance — the kind `security`
would catch instantly on seeing that proposal, and cannot catch otherwise, because in round 1 the
proposal does not exist yet — is missed. Round 2 recovers some of these, but only along the lines
synthesis already spotted a contradiction to chase; it cannot surface an interaction nobody
collided over.

This is the accepted cost of not running a round table, taken deliberately in exchange for the
independence that makes round 1 worth reading at all. The reasoning and the rejected alternative
are in decision D-019.
