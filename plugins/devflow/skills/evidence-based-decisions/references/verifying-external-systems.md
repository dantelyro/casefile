# Verifying external systems

How to establish what a system you do not control actually does, and how to be honest about
what you have not established.

## Find the machine-readable spec before reading prose

A spec fetched from the running system outranks any PDF. Before concluding one does not
exist, **vary the document-path convention** — hosts in the same product family often differ:

```
{base}/swagger/v1/swagger.json     # common
{base}/swagger/docs/v1             # older Swashbuckle — same words, transposed, no .json
{base}/openapi.json   {base}/v3/api-docs   {base}/api-docs
```

Sweep host × base-path × document-path. "Publishes no spec" has meant "we tried one naming
convention" often enough to be worth ruling out properly. A spec found this way frequently
settles a question that was quarantined as unknowable for weeks.

**Commit what you capture.** A spec in the repo is readable without credentials, a network
round trip, or a live environment — and it diffs when the vendor changes it.

## Probe before designing

One live call answers what an hour of reading guesses at. Design the probe to *distinguish*
outcomes, not merely to succeed:

- **Include a control** — a route you know exists. If your probe and the control fail
  identically, you have learned nothing about the probe.
- **Read the whole response shape**, not just the status: content-type, body, headers. A
  framework's routing 404 (JSON, "no resource matches this URI") and a web-server 404 (HTML)
  mean completely different things.
- **A non-obvious response is a lead, not noise.** A lone `501` among uniform `404`s meant
  "this service moved", with the new address in the body.

Read-only probes against a non-production environment are cheap. Say so explicitly when a call
mutates state, and get agreement first.

## An error proves reach, never pass

The most expensive inference pattern:

> "We got error X, which is checked *after* condition Y, therefore Y passed."

This is true only if you know the validation order — which you usually do not. Validations are
layered, and clearing one reveals the next. A rejection tells you which check you reached. It
says nothing about the checks behind it.

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
2. **A comment stating what it was derived from and how to confirm it.** Without this the next
   reader sees a plausible constant and assumes it is known-good.
3. **A test that fails if it changes** — written as a *literal*, never built from the constant.

Point 3 is what makes it a control rather than a note. The failure means "go re-confirm against
the real system", not "update the fixture to match the code".

## Capture live observations as fixtures

The moment a real response is observed, it becomes a permanent fixture — verbatim, with a
comment recording when and against what it was captured. Including the ugly ones: a
self-contradictory envelope, a misspelled field, an error message with a grammar mistake.
Those are the shapes a hand-written fixture will never contain, and they are exactly what
breaks a parser.

## Categories of unverified

Not all gaps are the same, and treating them alike hides the ones that matter.

| Category | Treatment |
|---|---|
| Guessed, confirmable later | Quarantine + change-detector test. Re-probe when unblocked |
| Tolerated both ways | No guess needed — handle both shapes. Often already closed |
| Unverifiable by policy | No test will ever settle it. Needs a documented first-call check at cutover |
| Unknown, needs discovery | Not a guess to quarantine — a fact to go find |

The third deserves its own decision entry. "We cannot check this without violating a safety
rule" is a distinct class from "not yet checked", and it recurs.

## Reporting status honestly

Report **built** and **verified** as separate axes. When a piece has only ever run against a
mock, say so in the same sentence that says it is merged. If a suite is intermittently red, say
that too — "green" from one run is luck, not a result.
