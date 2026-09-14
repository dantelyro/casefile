# The decision log

An append-only record of every non-trivial architectural or scope decision, with its reasoning
and the trade-offs accepted. Git already shows *what* was chosen. This records **why**, and **on
what evidence**, so a future reader can tell whether the reasoning still holds.

Everything below about content — entry shape, superseding, what earns an entry — holds whatever
the log is about. Layout is not a judgement call: one decision per file, from entry one.

## Layout

```
docs/
├── purpose.md               # what pain this solves, and what it is not
├── architecture/
│   └── mental-model.md      # what exists, where it lives, module state
└── decisions/               # sibling of architecture/
    ├── README.md            # generated index: id · title · status
    ├── 0001-hexagonal-architecture-ports-adapters.md
    ├── 0002-nestjs-on-fastify-not-express.md
    └── 0003-strict-typescript-esm-no-any.md
```

`NNNN-kebab-slug.md`, four digits, slug from the first eight words of the title. The file opens
with `# D-NNN — Title`, then the entry format below. The index is generated from the directory
and carries id, title, status and conventions only; the moment it holds reasoning there are two
places to update and they will disagree.

`decisions/` is a **sibling** of `architecture/` because they answer different questions: the
architecture document says what exists and where, the log says why and what was given up. The
log also covers scope, product and process choices no architecture document describes — which
plan to sell, whether to ship with payments simulated, who moderates what. Filed underneath, the
log reads as a subsection of the architecture, and the two start duplicating each other.

**One decision per file from entry one.** The split-later plan does not survive contact:

- **The threshold never trips.** "Split when it exceeds ~500 lines" needs someone to stop,
  measure, and choose migration over the task in front of them, so logs sail past it. One real
  log reached **886 lines** before anyone split it, by which point it was read with `grep` and
  line ranges rather than opened — the exact failure the limit was for.
- **Migration is strictly more work.** The same files get written either way, plus a bulk move
  and every cross-reference.
- **A `next id` pointer in a shared header is a contention point.** Here the highest filename
  *is* the pointer.

| Per-file layout buys | |
|---|---|
| Concurrent writers | Every entry is a new path, so no contention |
| Loading one decision | That file, not the whole history |
| Finding one by title | The filename is the title |
| Context cost | A few index lines per decision; bodies load on demand |

Cross-references cost a relative link resolved by the index. That is the whole price, and an
index pays it off immediately.

**Superseded entries stay in `decisions/`, under their original filename.** A superseded entry is
the most valuable thing in the log (see "Superseding, never deleting"), and an archive directory
breaks every `see D-NNN` aimed at it. The `Status` line is what marks it dead. Group a long index
by status.

## Entry format

```markdown
### D-042 — One-line statement of the decision, in the present tense
**Status:** Accepted (2026-08-06). | Open | **SUPERSEDED by D-047 (2026-09-01).**
**Decided by:** gabriel <gabriel@prover.net.br> — resolved by blaming the change. See
Attribution.
**Implemented by:** `992b19e` — omit while the decision is Open or unbuilt.
**Context:** The forcing question. What made a choice necessary, and what was known at the
time — including the evidence grade. "The manual documents X" and "a live probe returned X"
are different starting points and must read differently.
**Options:** (a) …; (b) …; (c) …. Real alternatives, not strawmen.
**Decision:** Which, and the reasoning that selected it.
**Trade-offs:** What was accepted by choosing it. If nothing was given up, the options were
not real.
**Changed by:**
- 2026-09-01 · gabriel — superseded by D-047; the premise about X was wrong.
- 2026-10-14 · marina — trade-offs extended: Y turned out to cost more than recorded.
```

Two optional closing sections earn their place when they apply:

- **The wider lesson, which outlives this entry** — when the finding generalises past the
  immediate decision.
- **The open question this exposes, deliberately not decided here** — surfaces a fork without
  pretending to resolve it.

## Attribution

**`Decided by`** names the person accountable for the choice. The field exists so a reader knows
**who to ask**, which makes a name nobody can source worse than useless.

**Resolve it by blaming the change the decision governs** — the implementing lines in the source.
On an append-only log, blaming the *entry* names whoever last amended it:

```bash
git log -L '/functionOrConstant/',+20:src/path/to/file.ts \
      --format='%H|%an <%ae>|%s' --no-patch \
  | grep -E '\|(feat|fix)(\(.+\))?!?:' | head -1
```

`git log -L` returns the history of just those lines, newest first. Filter to `feat` and `fix`:
decisions live there, while `docs`, `chore`, `style`, `test`, `ci` and `build` touch lines
without deciding anything — letting them through is how blame ends up naming whoever ran the
formatter. Read `refactor` as a second pass when `feat`/`fix` returns nothing for those lines: a
refactor is sometimes where a boundary was really drawn, and as often a move that decided
nothing. Widen the range to the file or directory when a decision spans more than a hunk, and
prefer the substantive change over a later touch-up.

**Most repos do not use conventional commits**, so an empty `grep` is the expected result rather
than a broken command. Check which convention the repo follows, then drop the filter and apply
the same judgement by hand:

```bash
git log -L '/functionOrConstant/',+20:src/path/to/file.ts \
      --format='%h|%an <%ae>|%s' --no-patch
```

Read down from newest and take the most recent subject that describes the decision you are
recording:

- `Turn listing deletion into finalize/reopen instead of a hard delete` — decides something.
  This is your commit.
- `Single R$49,90 plan for publishing a service; free plan has no post cap` — decides something.
- `Migrate backend to TypeScript (strict mode)` — touched the lines, decided nothing *about this
  entry*. A sweeping mechanical change sits on top of almost every line range; walk past it.
- `Up`, `wip`, `fixes` — describes nothing. Read the diff or keep walking back.
- `Add admin-content seed script; document connection_limit for shared Postgres` — mixed
  subject, half feature and half docs. Attribute on the half that touched *your* lines.

The oldest commit in the range is where the code was introduced, which is often — but not
always — where the choice was made. A decision later reversed or reshaped belongs to the commit
that reshaped it.

Blame gets you the author of the change. Where the choice belonged to someone else — landed on
another's behalf, or authorship rewritten by a rebase — name that person and say why in the body.
An entry attributed to the **agent** records nobody accountable; in an agent-assisted repo the
agent proposes and a human accepts, so blame names the human whose change carried it.

### Attribution has evidence grades too

Same ladder as the rest of this skill.

| Grade | Source of "who decided" | Trust |
|---|---|---|
| 1 | The person stated it — in the entry, a review, a message you can point at | Authoritative |
| 2 | Blame on the implementing `feat`/`fix`, or a PR approval that explicitly ratifies it | Strong |
| 3 | Commit authorship where the message shows *what* changed, not that it was chosen | Hypothesis |
| 4 | Inferred from repo shape — `git config`, sole committer, "who else would it be" | Worthless |

Grade 4 is seductive because it always produces a confident-looking name, and it has already
cost: seeding one backend log from `git config user.name` put the requester's name on 16 entries
whose 18 commits were authored by two entirely different people — and the log read as first-hand
throughout. A single-contributor repo does not make its one contributor the decider of everything
in it, and the contributor you assume is not reliably the one in the history.

**Mark a reconstructed entry as reconstructed.** A retroactively seeded log is a set of
hypotheses about intent, at whatever grade its evidence supports. Separate what you read from a
source comment or commit message — the author's own reasoning — from what you inferred, and leave
it to be confirmed. A reconstructed log is worth having, and worth less than a contemporaneous
one; the entry should show the difference.

**`Changed by`** — append-only: date, who, and *what changed*, one line per amendment. Omit the
field until there is a first amendment.

The trail matters more than it looks. An entry amended three times by three people is contested;
one nobody has revisited may simply be stale. Neither `Status` nor the body carries that, and git
history loses it the moment the file is reformatted. Never overwrite a `Changed by` line —
rewriting the record of who changed the record defeats the field.

## Numbering

Sequential `D-NNN`, matching the `NNNN-` filename, never reused. The highest filename in
`decisions/` is the pointer, so keep no `next id` anywhere:

```bash
ls docs/decisions/ | tail -1
```

Nothing to bump, nothing to contend over, and it cannot drift out of sync with reality.

Inserting between two existing ids — a decision that belongs beside `D-013` rather than at the
end — takes a letter suffix: `0013b-…`. It sorts directly after its neighbour, where renumbering
the tail would invalidate every `see D-NNN` in the repo.

## Superseding, never deleting

When an entry turns out to be wrong:

1. Mark it **SUPERSEDED by D-NNN** **on its `Status` line**, with a one-line summary of what was
   wrong. Leave the body intact and the file where it is. The `Status` line specifically: one
   decision per file means a reader opens that entry alone, with nothing around it, and a notice
   below the fold is invisible to exactly the reader most at risk of acting on a dead decision.
2. Append to its **`Changed by`** trail. Superseding is the most important thing that ever
   happens to an entry.
3. Write the new entry, stating what the old one got wrong and *why the reasoning failed*. Its
   `Decided by` is whoever made the *new* call, frequently not whoever made the old one, and that
   difference is worth being able to see.

The wrong turn is often the most valuable part of the record: it shows which evidence looked
convincing and was not, which is what stops the mistake recurring. A decision that reversed a
*correct* earlier belief deserves saying so plainly — "this reversed a correct earlier belief on
bad evidence" is worth more to a future reader than a tidy history.

## What earns an entry

**Yes:**
- A boundary, layer, or module shape
- Choosing between real alternatives with different costs
- A discovery that contradicts the documentation
- A constraint accepted deliberately (deferred work, a known gap)
- Anything a future reader might reasonably try to "fix" without knowing why it is that way

**No:**
- Anything git history or the code already states clearly
- Naming, formatting, ordinary refactors
- Restating a framework's documented behaviour

## Status values

| Status | Means |
|---|---|
| **Accepted** | Decided and in force |
| **Open** | The question is recorded, the answer is not |
| **Superseded by D-NNN** | Wrong or overtaken. Body preserved |

**Open** is not a failure state. "We do not know, here is the fork, here is why it was not
decided today" is more useful than a decision invented to close the entry.

## Linking a decision to its code

`Implemented by` closes the loop between reasoning and artefact, and answers two questions
nothing else in the repo answers:

- **Was this ever actually built?** An entry reading *Accepted* for months with no implementing
  commit was either forgotten or never really decided. Both are worth knowing.
- **Did the code drift from the decision?** `git log <sha>..HEAD -- <paths>` shows everything
  that touched the same area afterwards, which is where silent divergence lives.

Add it when the implementing change lands — you do not have the SHA before then, and a
back-filled guess is worse than an absent field. Keep the date on the `Status` line, because
rebase rewrites SHAs and the entry has to stay locatable when the hash stops resolving.

## Keeping it honest

- Record the decision **in the same change** that implements it. Reasoning written a week later
  is reconstruction.
- If an entry's *premise* turns out wrong, correct the premise and keep the reasoning visible
  rather than quietly rewriting it into correctness.
- Cross-reference: `see D-036` beats restating.
