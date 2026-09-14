# The output documents

Phase 7 turns the synthesis into three files on disk: what the project is for, what it must do, and
the record of how those two were arrived at. Each is offered and each can be declined separately.

## `docs/purpose.md`

The pain, who has it, and the non-goals.

It is written **twice** — drafted in phase 2 from the brief, refined here in phase 7 — and the
duplication is deliberate rather than a missed consolidation:

- **Early**, because the client cast is derived from it and every actor needs something to argue
  against. A purpose written after the round is a summary of what the actors said, which makes it
  unfalsifiable: nothing in the round could ever have contradicted it.
- **Late**, because that argument is what sharpens it. The round routinely establishes that the
  pain was described one layer too high, that a named party has no stake after all, or that
  something assumed in-scope was never wanted by anyone.

The refined version replaces the draft in place. The line above is the headline only; the content
rule it comes from — what belongs in purpose and what does not — is **D-011**'s, and is not
reproduced here.

## `docs/requirements.md`

Two sections, stable ids so decisions and tests can cite them:

- **Functional (`F-NN`)** — what it must do, phrased so a test can fail. "Users can reset a
  password without support" is a requirement; "good password handling" is not.
- **Non-functional (`N-NN`)** — what it must hold true under: latency, availability, data
  residency, budget, compliance. **Each carries a number.** "Fast" is not a requirement, and an
  unnumbered one cannot be violated, only disappointed.

Mark each `must` or `should`, and say which are unverified. Non-functional requirements are the
ones most often asserted and never measured.

That format is this skill's to state — **D-011b**, superseded by **D-023**, moved it here when
`evidence-based-decisions` stopped claiming the document. On top of it this skill adds two things:

- **Every line is attributed** to the actor that raised it, and carries its claim tag.
- **The file splits into `In the MVP` and `Cut`**, and a cut line keeps both its reason and its
  advocate.

**Why the cut section exists at all.** A cut requirement with its advocate named is what stops the
same argument being had again in six weeks — someone proposes the feature, the file says who wanted
it, why it lost, and what would change the answer, and the conversation resumes instead of
restarting. And a requirements file listing only what survived looks like it was never contested:
the reader cannot tell an MVP that was cut down from a feature list nobody challenged, which are
the two things this skill exists to distinguish.

The shape:

```markdown
## In the MVP
- F-01 Log an entry offline; sync when connectivity returns.
  [reasoned — architect, backend, frontend, independently]

## Cut
- F-12 Client billing. [claimed — UNVERIFIED — Ray, commercial guide]
  Cut: the only advocate is the one commercial operator in the cast, and it
  serves his business model rather than the stated purpose. Revisit if a real
  operator confirms it.

## Unverified claims — confirm before designing around these
- "No signal in the field." [claimed — UNVERIFIED — all domain actors]
```

Two details in that example are worth reading off it. `independently` on F-01 records that three
actors reached it blind, which is the strongest signal round 1 can produce and is lost the moment
the attribution is compressed to a count. And the cut line names **what would reverse it** — a cut
whose revisit condition is stated is a decision; one without is an omission that will be argued
from scratch.

## `docs/discovery/YYYY-MM-DD-<topic>.md`

The session record. Sections: the brief verbatim · the cast and why each actor was in it · what
clashed and how round 2 resolved it (or that it is still held) · what is still undecided.

Unverified claims are **not** among them. They are quarantined in `docs/requirements.md`, in the
section above, because that is the file they are being kept out of — a second copy here would be
the one still asserting a claim after the first was confirmed and promoted.

**Distilled, not dumped.** A full cast's raw round-1 prose is thousands of lines that get read
once. What belongs here is the positions and the reasons, not the transcripts that carried them.

Its job is distinct from the other two, which is why it is a third file rather than an appendix to
either: it is the only document that says **why a requirement exists and who wanted it**. That is
exactly what a future reader needs before deleting one — `requirements.md` tells them the line is
there, and only the discovery record tells them whether removing it costs anyone anything.

Dated and topic-named because a project runs this skill more than once. A second discovery session
is a new file beside the first, not an edit to it; the first record stayed true about the day it
was written, and overwriting it destroys the only account of a decision that has since been
reversed.

## Nothing is written unasked

`SKILL.md` states the rule. Applied here it means each of the three is offered **separately** —
declining the requirements file does not decline the discovery record, and a project that wants
only the session record gets only the session record.

## Handing off

Setting the initial reconciliation watermark to `HEAD` and seeding `docs/decisions/` belong to
`evidence-based-decisions`, not to this skill. Its
`references/decision-log.md` carries the log format and the entry template; use it there, and do
not restate either here (D-008).

One loop crosses the boundary and is worth naming so it is not left to chance. Promoting a
`[claimed — UNVERIFIED]` line into a requirement, once a real person has confirmed it, **is a
decision entry** — recorded with the new grade the confirmation earned, so the requirement stops
carrying the tag and the reason it stopped is on the record. That entry is written under the other
skill's rules; this one only says when it is owed.

The hand-off forward is `project-specs`: this skill ends with documents and no project. The full
ordering — and where `/init` falls in it — is stated once, in `skills/mvp/SKILL.md`.
