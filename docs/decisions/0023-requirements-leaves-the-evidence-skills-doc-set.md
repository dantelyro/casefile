# D-023 — Requirements leaves the evidence skill's doc set

**Status:** Accepted (2026-09-14). Supersedes **D-011b**.
**Decided by:** dantelyro <contas@prover.net.br> — Grade 1: decided in session.
**Implemented by:** this change.

**Context:** **D-011b** put `docs/requirements.md` in the set `evidence-based-decisions` proposes,
seeds and reconciles. **D-020** later split the seeding path by evidence grade: a repo with code is
Grade 1–2 — layout, stack and entry points are on disk — so that path stayed here, while seeding
from a cast of actors is unsourced by construction and went to `mvp`.

D-020 split the *path*. It did not re-run its own test against the *documents* on that path, and one
of them does not survive it.

**Options:** (a) leave it, and accept a seeding path that offers a document it cannot source;
(b) keep the row in "The set" but mark it seed-never, reconcile-always; (c) remove
`docs/requirements.md` from the skill entirely, moving the `F-NN`/`N-NN` format to `mvp` with it.

**Decision:** (c). Layout, stack and entry points are observable; **a requirement is not**. Code
shows what a system does, never what it is obliged to do, and the gap between those two is the
entire content of a requirements file. Deriving one from source is Grade 4 — inference from the
absence of a contradiction — which this skill's own ladder calls nearly worthless. The seeding path
could never have produced a requirement honestly; it had been offering to seed a document it has no
evidence for.

`mvp` produces the same file from a cast, tags every line `[reasoned]` or `[claimed — UNVERIFIED]`,
and quarantines it until a person confirms it. That is the discipline an unsourced requirement
needs, and the one `evidence-based-decisions` does not carry.

(b) was rejected because a row in "The set" is an ownership claim as much as a reconciliation
instruction — the skill that lists a document is the skill that seeds it when it is missing, which
is the behaviour being removed. A row reading "owned by `mvp`, reconcile but never seed" asks the
model to hold a distinction the rest of the table does not draw, in the one document whose seeding
trigger already fires too easily.

The format **moved rather than being deleted**. `mvp/references/documents.md` deferred upward for
`F-NN`/`N-NN` and the number-on-every-non-functional rule; deleting the section it pointed at would
have left `mvp` deferring to a decision entry with no skill file behind it — a reader following the
pointer lands in this repo's history instead of a project's instructions. Stated once, now in the
skill that owns it (**D-008**).

**Trade-offs:** `docs/requirements.md` leaves what this skill **reconciles**, not just what it
seeds. In a project where `mvp` wrote one, nothing afterwards checks it against the code that has
since landed — and D-011b names that cost precisely: *requirements rot faster than anything else in
the set*. This removes the only mechanism that was slowing that rot, in exchange for never again
seeding a requirement nobody sourced. Recorded so the next reader can tell it was priced rather
than overlooked; a future entry re-adding a reconcile-only row has the (b) paragraph to argue
against.

`docs/discovery/` stays in the set, the row directly below the one removed, and the decision not to
take it with requirements is deliberate. Its subject is why something was wanted and what was cut
with whom advocating for it — the decision log's territory rather than the requirements file's — and
it is what a superseding entry cites when a requirement is renegotiated. It points at a document
rather than claiming a format, so it still reads correctly. This is the weakest paragraph here: if
the seeding trigger proves to fire on `docs/discovery/` in practice, that row comes out too.

**The wider lesson, which outlives this entry:** a rule that splits a *path* by evidence grade has
to be re-run against every *document* on that path. D-020 got the split right and left one document
standing on the wrong side of it, because splitting the path felt like finishing the job.
