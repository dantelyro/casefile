---
name: evidence-based-decisions
description: >
  Use at the START of any session on a project that keeps a decision log, architecture
  document, or mental-model file — and when initializing a new project or running /init, or
  when a project has no such docs yet. Also use when building against a system you do not
  control (third-party or government API, vendor SDK, undocumented protocol). Triggers on:
  starting work after someone else has committed, vendor docs disagreeing with observed
  behaviour, a green test suite that failed in production anyway, deciding whether something
  is "done", recording why an approach was chosen, superseding an earlier decision, or a claim
  in a project document turning out to be false.
---

# Evidence-Based Decisions

## Overview

When you integrate with a system you do not control, the expensive failures are not bugs.
They are **confident false beliefs** — a documented endpoint that does not exist, a green
suite asserting against a response you invented, a conclusion drawn from an error you did
not receive.

**Core principle: grade your evidence, and record the grade.** Every claim about an external
system carries a strength. Writing it down is what stops the next person — including you —
from treating a guess as a fact.

## The evidence ladder

Strongest to weakest. Never let a lower rung override a higher one.

| Grade | Source | Trust |
|---|---|---|
| 1 | Live response from the real system | Authoritative |
| 2 | Machine-readable spec fetched from that system (OpenAPI, XSD pattern, `.proto`) | Strong |
| 3 | Prose documentation — PDF manuals, wiki pages, annotations | **Hypothesis only** |
| 4 | Inference from the *absence* of an error | Nearly worthless |

Grade 3 has been wrong repeatedly and confidently. Grade 4 is how the worst mistakes happen:
an error code proves you reached **that** check, never that you passed the ones after it.

**When prose and a machine-readable spec disagree, the spec wins** — including inside one
document, where prose annotation contradicts the pattern beside it.

## Start of session: reconcile before anything else

The docs describe the code **as of the last time someone reconciled them**. Other people commit
without an agent, so that is not the same as "now".

Every doc-updating change records the commit it was reconciled through. At session start,
replay what has happened since:

```bash
git log --oneline <watermark>..HEAD -- <source paths>
```

- **Empty** — docs are current. Proceed.
- **Non-empty** — those commits are unreviewed. Read them, update whatever they invalidated,
  and move the watermark.

Without the watermark you are guessing at what changed, and the usual guess — "probably
nothing" — is how docs quietly go stale. Full mechanism, including how it breaks:
`references/living-documents.md`.

## No docs yet? Offer to bootstrap — do not assume

On a new project, or one with no architecture doc or decision log, **propose the set and ask**
before creating anything. A project may deliberately keep this elsewhere, or not want it.

Say what each file is for and what it costs. If accepted, seed them from what the repo already
shows — layout, stack, entry points — and set the initial watermark to `HEAD`. Do not invent
decisions that were never made; an empty log with a numbering convention is the correct
starting state.

## The loop

1. **Read the record first** — decision log, architecture doc, project instructions. A finding
   that contradicts a logged decision is a discussion, not a silent override.
2. **Probe before designing.** One live call against the real system beats an hour of reading.
   Capture what comes back; it becomes your fixture.
3. **Build, with unverified values quarantined** — named constants, one call site, a comment
   saying what they were derived from and how to confirm them.
4. **Record the decision** with its evidence grade. See `references/decision-log.md`.
5. **Verify, and say which axis you verified.** See `references/verifying-external-systems.md`.
6. **When a claim proves false, correct it everywhere** — then sweep for the same claim
   elsewhere. See `references/living-documents.md`.

## Built is not verified

Track two axes separately. Collapsing them is the single most costly habit this skill exists
to prevent.

- **Built** — the code exists, tests pass.
- **Verified** — a real response from the real system confirmed the contract.

A suite can be 100% green across weeks of review and completely broken against the live API.
State both when reporting status: *"merged, mocks only"* is honest; *"done"* is not.

## Never derive a fixture from the code under test

```js
// ❌ cannot fail — asserts "we read the field we wrote"
.reply(200, { [RESPONSE_FIELD]: value })

// ✅ literal — goes red if the constant drifts
.reply(200, { actualFieldName: value })
```

The same trap in another guise: a test that passes because both sides share a wrong default.
If a fixture and the implementation can only agree, the test proves nothing.

## Stop guessing after two failed diagnoses

Two wrong theories in a row means **measure instead**. Sample the actual state — connection
counts, timings, memory, the raw response body. Then write both dead ends into the commit so
the next attempt does not repeat them.

## Red flags — stop and get evidence

- "The manual says…" as the basis for building
- "It must be X, because we didn't get error Y"
- A test that passes when you break the thing it covers
- "All tests are green" offered as proof the integration works
- Reporting a piece as done when it has only ever seen a mock
- A doc claim you know is false, left because correcting it wasn't the task
- Starting work without checking what landed since the docs were last reconciled
- Creating an architecture doc or decision log on a project that never asked for one

## Rationalizations

| Excuse | Reality |
|---|---|
| "The official docs are authoritative" | They are a hypothesis. Vendor prose has been wrong repeatedly; the machine-readable spec has not. |
| "Probing costs a round trip" | One probe costs minutes. Building on a wrong assumption costs the rebuild plus everything layered on it. |
| "The suite is green, so it works" | Green means self-consistent. Mocks cannot verify a contract they define. |
| "It's documented nowhere" | Check the *other* path convention before concluding that. Specs hide behind naming differences. |
| "I'll record the decision later" | The reasoning is gone by then. What survives is the conclusion, with no way to tell if it still holds. |
| "Correcting that doc isn't my task" | A known-false doc actively misleads whoever reads it next, who will not have your context. |
| "Rewriting the wrong entry is cleaner" | The wrong turn is the most valuable part of the record. Supersede; never delete. |
| "The docs were fine last session" | Other people commit without an agent. Replay `watermark..HEAD` — it takes one command and is the only way to know. |
| "Nothing's changed since last time" | That is the guess the watermark exists to replace. Run it. |
| "Every project should have a decision log" | Propose, then ask. Creating docs a team never wanted produces files nobody maintains, which is worse than none. |

## References

- `references/decision-log.md` — entry format, superseding, what earns an entry
- `references/verifying-external-systems.md` — probing, capturing specs, quarantining unknowns
- `references/living-documents.md` — architecture docs and project instructions as source of truth
