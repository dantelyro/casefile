---
name: evidence-based-decisions
description: >
  Use at the start of a session in a project that keeps a decision log, architecture document
  or reconciliation watermark; when initialising a project that keeps none of them (/init); or
  when building against a system you do not control — third-party or government API, vendor
  SDK, undocumented protocol. Triggers on: picking up work after someone else has committed,
  vendor docs disagreeing with observed behaviour, a green test suite that failed in production
  anyway, deciding whether something is "done", recording why an approach was chosen,
  superseding an earlier decision, or finding a claim in a project document that is false.
model: sonnet
---

# Evidence-Based Decisions

## Overview

When you integrate with a system you do not control, the expensive failures are not bugs.
They are **confident false beliefs** — a documented endpoint that does not exist, a green
suite asserting against a response you invented, a conclusion drawn from an error you never
received.

**Core principle: grade your evidence, and record the grade.** Every claim about an external
system carries a strength. Writing it down is what stops the next reader — including you —
from taking a guess for a fact.

## The evidence ladder

A lower rung never overrides a higher one.

| Grade | Source | Trust |
|---|---|---|
| 1 | Live response from the real system | Authoritative |
| 2 | Machine-readable spec fetched from that system (OpenAPI, XSD pattern, `.proto`) | Strong |
| 3 | Prose documentation — PDF manuals, wiki pages, annotations | **Hypothesis only** |
| 4 | Inference from the *absence* of an error | Nearly worthless |

Grade 3 has been wrong repeatedly and confidently, so when prose and a machine-readable spec
disagree the spec wins — including inside a single document, where an annotation contradicts
the pattern printed beside it. Grade 4 is where the worst mistakes start: an error code proves
you reached **that** check and says nothing about the checks behind it.

## Session start: reconcile

Docs describe the code as of the last reconciliation. People commit without an agent, so that
is not the same as now.

Every doc-updating change records the commit it was reconciled through. Replay the gap:

```bash
git log --oneline <watermark>..HEAD -- <source paths>
```

**Empty** — the docs are current, proceed. **Non-empty** — those commits are unreviewed: read
them, update whatever they invalidated, and move the watermark in the same commit as the doc
update. "Probably nothing changed" is the guess the watermark exists to replace; the command
takes one second. Full mechanism, including recovery when the SHA stops resolving:
`references/living-documents.md`.

## No docs yet: propose, then ask

A project with no project instructions, architecture document or decision log may keep this
material elsewhere, or want none of it. Say what each file is for and what it costs, and wait
for an answer — files nobody wanted are worse than no files.

**Two cases, and the split is itself an evidence grade.**

- **Code exists, docs do not.** This path, unchanged. Seed from what the repo shows — layout,
  stack, entry points. That is Grade 1 and 2 evidence, and it beats any actor's account of what
  the project probably is.
- **No code, no docs.** Hand to `mvp`. There is nothing to read, so a cast of actors is the best
  available source — and everything it produces is unsourced until a person confirms it, which is
  why that skill tags every line it emits.

Seeding an empty directory from this skill would replace the better-evidenced path with the worse
one, which is the mistake this entire skill exists to prevent.

**Run `/init` first.** Project instructions come before the rest of the set: they are the only
document every session loads, so a log created without them is a log nothing points at. Then
`docs/purpose.md` — what the project is for — before the architecture document, which describes a
shape that only makes sense once that is settled.

**`docs/requirements.md` is never seeded here**, on either branch. Layout, stack and entry points
are observable on disk; a `must` is not. Code shows what a system does, never what it is obliged to
do, so reading a requirement off an implementation is Grade 4. `mvp` owns that document, with the
tagging and quarantine discipline an unsourced requirement needs.

Once accepted, seed from what the repo already shows — layout, stack, entry points — set the
initial watermark to `HEAD`, and start the log as `docs/decisions/NNNN-slug.md`, one decision
per file, with a generated `docs/decisions/README.md` index. `decisions/` sits **beside**
`architecture/`: the architecture document says what exists and where, the log says why and
what was given up, and the log covers scope and product choices no architecture document
describes. Both the layout and the placement are fixed from entry one — see
`references/decision-log.md`.

An empty log with a numbering convention is the correct starting state; invent no decisions to
fill it. Every seeded entry is a **reconstruction**: mark it as one, and resolve `Decided by`
by blaming the `feat`/`fix` commit that implemented the change. Whoever asked you for the
documentation is rarely whoever made the call, and the entry reads as first-hand either way.
See "Attribution" in `references/decision-log.md`.

## The loop

1. **Read the record first** — decision log, architecture document, project instructions. A
   finding that contradicts a logged decision is a discussion, not a silent override.
2. **Probe before designing.** One live call answers what an hour of reading guesses at, and
   costs minutes against a rebuild plus everything layered on top of a wrong assumption.
   Capture what comes back; it becomes your fixture.
3. **Build, with unverified values quarantined** — named constants, one call site, a comment
   saying what they were derived from and how to confirm them.
4. **Record the decision** with its evidence grade, as a new file in `decisions/`. See
   `references/decision-log.md`.
5. **Verify, and say which axis you verified.** See `references/verifying-external-systems.md`.
6. **When a claim proves false, correct it everywhere** — immediately, as its own concern, then
   sweep for the same claim elsewhere. See `references/living-documents.md`.

## Built is not verified

Two separate axes. Collapsing them is the single most costly habit this skill exists to
prevent.

- **Built** — the code exists, tests pass.
- **Verified** — a real response from the real system confirmed the contract.

A suite can be green across weeks of review and completely broken against the live API. State
both when reporting status: *"merged, mocks only"* is honest, *"done"* is not.

## Never derive a fixture from the code under test

```js
// ❌ cannot fail — asserts "we read the field we wrote"
.reply(200, { [RESPONSE_FIELD]: value })

// ✅ literal — goes red if the constant drifts
.reply(200, { actualFieldName: value })
```

Same trap in another guise: a test that passes because both sides share a wrong default. If a
fixture and the implementation can only agree, the test proves nothing.

## Stop guessing after two failed diagnoses

Two wrong theories in a row means **measure instead**. Sample the actual state — connection
counts, timings, memory, the raw response body — then write both dead ends into the commit so
the next attempt does not repeat them.

## Red flags — stop and get evidence

- "The manual says…" as the basis for building
- "It must be X, because we didn't get error Y"
- A test that still passes when you break the thing it covers
- "All tests are green" offered as proof the integration works
- Reporting a piece as done when it has only ever seen a mock
- A doc claim you know is false, left because correcting it wasn't the task
- A `Decided by` name that came from `git config` rather than from blame

## Rationalizations

| Excuse | Reality |
|---|---|
| "The official docs are authoritative" | They are a hypothesis. Vendor prose has been wrong repeatedly; the machine-readable spec has not. |
| "The suite is green, so it works" | Green means self-consistent. Mocks cannot verify a contract they define. |
| "It's documented nowhere" | Check the *other* path convention first. Specs hide behind naming differences. |
| "I'll record the decision later" | By then the reasoning is gone and only the conclusion survives, with no way to tell if it still holds. |
| "One file is fine for now, I'll split it later" | Nobody splits later; one real log hit 886 lines first. |
| "Someone has to go in `Decided by`" | A name you cannot source reads as first-hand. Blame the change, or mark the entry reconstructed. |

## References

- `references/decision-log.md` — layout, entry format, attribution, superseding, what earns an
  entry
- `references/verifying-external-systems.md` — probing, capturing specs, quarantining unknowns
- `references/living-documents.md` — architecture docs and project instructions as source of
  truth
