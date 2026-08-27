# Verifying external systems

How to establish what a system you do not control actually does, and how to be honest about what
you have not established.

## Find the machine-readable spec before reading prose

A spec fetched from the running system outranks any PDF. Before concluding one does not exist,
**vary the document-path convention** — hosts in the same product family often differ:

```
{base}/swagger/v1/swagger.json     # common
{base}/swagger/docs/v1             # older Swashbuckle — same words, transposed, no .json
{base}/openapi.json   {base}/v3/api-docs   {base}/api-docs
```

Sweep host × base-path × document-path. "Publishes no spec" has meant "we tried one naming
convention" often enough to be worth ruling out properly, and a spec found this way frequently
settles a question that was quarantined as unknowable for weeks.

**Commit what you capture.** A spec in the repo is readable without credentials, a network round
trip, or a live environment — and it diffs when the vendor changes it.

## Probe before designing

One live call answers what an hour of reading guesses at. Design the probe to *distinguish*
outcomes rather than merely to succeed:

- **Include a control** — a route you know exists. Probe and control failing identically teaches
  you nothing about the probe.
- **Read the whole response shape**: status, content-type, body, headers. A framework's routing
  404 (JSON, "no resource matches this URI") and a web-server 404 (HTML) mean completely different
  things.
- **A non-obvious response is a lead, not noise.** A lone `501` among uniform `404`s meant "this
  service moved", with the new address in the body.

Read-only probes against a non-production environment are cheap. Where a call mutates state, say
so explicitly and get agreement first.

## An error proves reach, never pass

The most expensive inference pattern:

> "We got error X, which is checked *after* condition Y, therefore Y passed."

True only if you know the validation order, which you usually do not. Validations are layered, and
clearing one reveals the next. A rejection tells you which check you reached and nothing about the
checks behind it.

**Map the order empirically** by clearing each layer and recording what surfaces:

```
E0008  date not in the future
  ↓
E0370  required group missing        ← cleared by implementing it
  ↓
E0312  service administered here     ← revealed only after the above
  ↓
E0084  emitter established here      ← the real blocker, invisible until now
```

Until that map exists, "the remaining blocker is X" is unsupportable from any single rejection.

## Quarantining what you cannot verify

When a value must be guessed to make progress:

1. **A named exported constant**, referenced from exactly one place.
2. **A comment stating what it was derived from and how to confirm it.** Without it, the next
   reader sees a plausible constant and assumes it is known-good.
3. **A test that fails if it changes** — written as a *literal*, never built from the constant.

Point 3 is what makes it a control rather than a note. Its failure means "go re-confirm against the
real system", not "update the fixture to match the code".

## Capture live observations as fixtures

The moment a real response is observed it becomes a permanent fixture — verbatim, with a comment
recording when and against what it was captured. Including the ugly ones: a self-contradictory
envelope, a misspelled field, an error message with a grammar mistake. Those are the shapes a
hand-written fixture never contains, and exactly what breaks a parser.

## Categories of unverified

Not all gaps are the same, and treating them alike hides the ones that matter.

| Category | Treatment |
|---|---|
| Guessed, confirmable later | Quarantine + change-detector test. Re-probe when unblocked |
| Tolerated both ways | No guess needed — handle both shapes. Often already closed |
| Unverifiable by policy | No test will ever settle it. Needs a documented first-call check at cutover |
| Unknown, needs discovery | Not a guess to quarantine — a fact to go find |

The third deserves its own decision entry. "We cannot check this without violating a safety rule"
is a distinct class from "not yet checked", and it recurs.

## Reporting status honestly

Report **built** and **verified** as separate axes, in the same sentence: a piece that has only run
against a mock says so where it says it is merged. An intermittently red suite gets said too —
"green" from one run is luck, not a result.
