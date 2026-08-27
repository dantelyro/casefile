# The decision log

An append-only record of every non-trivial architectural or scope decision, with its reasoning
and the trade-offs accepted.

Its job is not to record *what* was chosen. Git shows that. Its job is to record **why**, and
**on what evidence**, so a future reader can tell whether the reasoning still holds.

Everything below about **content** — the entry shape, superseding, what earns an entry — holds
whatever the log is about. **Layout is not a judgement call: one decision per file, always.**

## One decision per file — not conditional

```
docs/
├── architecture/
│   └── mental-model.md      # what exists, where it lives, module state
└── decisions/               # SIBLING of architecture/, never nested inside it
    ├── README.md            # generated index: id · title · status. Never entry bodies
    ├── 0001-hexagonal-architecture-ports-adapters.md
    ├── 0002-nestjs-on-fastify-not-express.md
    └── 0003-strict-typescript-esm-no-any.md
```

`NNNN-kebab-slug.md`, four digits, slug from the first eight words of the title. The file opens
with `# D-NNN — Title` and then the entry format below. The index is generated from the
directory and holds **only** id, title, status and conventions — the moment it holds reasoning,
there are two places to update and they will disagree.

**`decisions/` is a sibling of `architecture/`, not a child.** They answer different questions
and the doc set treats them as separate living documents: the architecture doc says *what exists
and where*, the log says *why, and what was given up*. Nesting the log under `architecture/`
implies decisions are a subsection of the architecture, and they are not — a log covers scope,
product and process choices that no architecture doc describes (which plan to sell, whether to
ship with payments simulated, who moderates what). Putting them in a subdirectory of the thing
they are not about is how the two start duplicating each other.

**Start here on entry one.** Do not begin with a single file intending to split later:

- **The threshold never trips in practice.** "Split when it exceeds ~500 lines" is a rule that
  requires someone to stop, measure, and choose migration over the task in front of them.
  Nobody does that, so logs sail past the limit — one real project reached **886 lines** before
  anyone split it, by which point the log was being read with `grep` and line ranges rather than
  opened, which is the failure the limit was meant to prevent.
- **Migration is strictly more work than starting split.** The same files get written either
  way; doing it later adds a bulk move plus every cross-reference.
- **A "next id" pointer in a shared header is a contention point.** Under this layout the
  highest filename *is* the pointer, so there is no shared line to conflict over.

What the layout buys, and why it is worth the extra file:

| | One decision per file |
|---|---|
| Concurrent writers | No contention — every entry is a new path |
| Loading one decision | Just that file, not the whole history |
| Finding one by title | The filename *is* the title |
| Context cost | The index is a few lines per decision; bodies load on demand |
| Cross-references | A relative link, resolved by the index |

The last row is the only genuine cost, and an index pays it off immediately.

**Superseded entries stay in `decisions/`.** Do not move them to an archive directory to keep
the active set small — a superseded entry is the most valuable thing in the log (see
"Superseding, never deleting"), and relocating it breaks every `see D-NNN` pointing at it. Its
`Status` line is what marks it dead; the filename never changes. If the index gets long, group
it by status, never by trimming it.

## Entry format

```markdown
### D-042 — One-line statement of the decision, in the present tense
**Status:** Accepted (2026-08-06). | Open | **SUPERSEDED by D-047 (2026-09-01).**
**Decided by:** gabriel <gabriel@prover.net.br> — resolved by blaming the change, not by
whoever is running the session. See Attribution.
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

## Attribution

**`Decided by`** — the person accountable for the choice. The point of the field is knowing
**who to ask**, so it has to name whoever actually made the call.

**Never take it from `git config user.name`.** That names whoever is at the terminal right now.
When an entry is written after the fact — seeding a log for an existing repo, reconciling a
watermark — that is *the person who asked for the documentation*, which is a different role
from the person who decided. Substituting one for the other manufactures accountability: it
puts a name against a choice they may never have made, and it reads as a first-hand record.

**Resolve it by blaming the change the decision governs** — the lines that implement it, in the
source, not in this log. On an append-only log, blaming the *entry* points at whoever last
amended it, which is why the target is always the implementing code:

```bash
git log -L '/functionOrConstant/',+20:src/path/to/file.ts \
      --format='%H|%an <%ae>|%s' --no-patch \
  | grep -E '\|(feat|fix)(\(.+\))?!?:' | head -1
```

`git log -L` returns the history of just those lines, newest first.

**Filter to the commits that actually made the code — `feat` and `fix`.** Those are where
decisions live. `docs`, `chore`, `style`, `test`, `ci` and `build` touch lines without deciding
anything, and letting them through is how blame ends up naming whoever ran the formatter.
Include `refactor` as a second pass when `feat`/`fix` returns nothing for those lines: a
refactor can be where a boundary was really drawn, but it is as often a move that decided
nothing — read the commit before accepting it.

Widen the range to the file or directory when a decision spans more than a hunk, and prefer the
substantive change over a later touch-up.

**If the commits carry no prefix, blame by the commit description instead.** Most repos do not
use conventional commits, so the `grep` returning nothing is the expected result, not a broken
command — check which convention a repo follows before trusting a type filter over it. Drop the
filter, read the subject lines, and apply the same judgement by hand: does this subject describe
a change to behaviour, or only to presentation?

```bash
git log -L '/functionOrConstant/',+20:src/path/to/file.ts \
      --format='%h|%an <%ae>|%s' --no-patch
```

Newest first. Read down the list and take the most recent subject that describes the decision
you are recording:

- `Turn listing deletion into finalize/reopen instead of a hard delete` — decides something.
  This is your commit.
- `Single R$49,90 plan for publishing a service; free plan has no post cap` — decides something.
- `Migrate backend to TypeScript (strict mode)` — touched the lines, decided nothing *about this
  entry*. A sweeping mechanical change will sit on top of almost every line range; skip past it.
- `Up`, `wip`, `fixes` — describes nothing. Read the diff or keep walking back.

Beware the mixed subject: `Add admin-content seed script; document connection_limit for shared
Postgres` is half feature, half docs. Attribute on the half that touched *your* lines.

The oldest entry in the range is where the code was introduced, which is often — but not
always — where the choice was made. A decision that was later reversed or reshaped belongs to
the commit that reshaped it.

Two further things this field is **not**:

- **Not the committer, when they diverge.** Someone lands a decision on another's behalf; a
  rebase rewrites authorship. Blame gets you the author of the change; where you know the
  choice belonged to someone else, name that person and say why in the body.
- **Not the agent.** An entry attributed to a tool records nobody accountable. But do not
  invert this into "so the human's git identity must be right" — that inference is the whole
  trap above. In an agent-assisted repo the agent proposes and a human accepts, and blame names
  the human whose change carried it.

### Attribution has evidence grades too

Same ladder as the rest of this skill; never let a lower rung override a higher one.

| Grade | Source of "who decided" | Trust |
|---|---|---|
| 1 | The person stated it — in the entry, a review, a message you can point at | Authoritative |
| 2 | Blame on the implementing `feat`/`fix`, or a PR approval that explicitly ratifies it | Strong |
| 3 | Commit authorship where the message only shows *what* changed, not that it was chosen | Hypothesis |
| 4 | Inferred from repo shape — `git config`, sole committer, "who else would it be" | Worthless |

Grade 4 is seductive because it always produces a confident-looking name.

> **This has already happened.** Seeding a log for a backend, every entry was attributed from
> `git config user.name` to the person who requested the docs. Blame showed all 18 commits were
> authored by two entirely different people. Sixteen entries named someone who had made none of
> the decisions — and the log read as first-hand throughout. A single-contributor repo does not
> make its one contributor the decider of everything in it, and the contributor you assume is
> not reliably the one in the history.

**When an entry is reconstructed rather than recorded, say so in the entry.** A retroactively
seeded log is a set of hypotheses about intent, at whatever grade its evidence supports. Mark
which parts are read from a source comment or commit message — the author's own reasoning — and
which are your inference, and leave the reconstruction to be confirmed rather than presenting it
as first-hand. A reconstructed log is worth having; it is not worth as much as a contemporaneous
one, and the entry should not blur the difference.

**`Changed by`** — an append-only trail. One line per amendment: date, who, and *what changed*.
Omit the field entirely until there is a first amendment; an empty heading is noise.

The trail matters more than it looks. A decision that has been amended three times by three
people is a different object from one nobody has revisited — the first is contested, the second
may simply be stale. Neither `Status` nor the body carries that, and git history loses it the
moment the file is reformatted.

Never overwrite a `Changed by` line. Rewriting the record of who changed the record defeats
the whole field.

Optional closing sections that earn their place:

- **The wider lesson, which outlives this entry** — when the finding generalises past the
  immediate decision.
- **The open question this exposes, deliberately not decided here** — surfaces a fork without
  pretending to resolve it.

## Numbering

Sequential `D-NNN`, matching the `NNNN-` filename, never reused.

**Keep no `next id` pointer anywhere.** The highest filename in `decisions/` is the pointer:

```bash
ls docs/decisions/ | tail -1
```

Nothing to bump, nothing to contend over, and it cannot drift out of sync with reality.

Inserting between two existing ids — a decision that belongs beside `D-013` rather than at the
end — takes a letter suffix: `0013b-…`. It sorts directly after its neighbour, and renumbering
the tail would invalidate every `see D-NNN` in the repo.

## Superseding, never deleting

When an entry turns out to be wrong:

1. Mark the old one **SUPERSEDED by D-NNN** **on its `Status` line**, with a one-line summary of
   what was wrong. Leave the body intact, and leave the file where it is.

   On the `Status` line specifically, not in a banner further down: one decision per file means
   a reader can open that entry alone, with nothing around it, and the status is the first thing
   they must see. A supersession notice below the fold is invisible to exactly the reader most
   at risk of acting on a dead decision.
2. Append to its **`Changed by`** trail — date, who, what changed. Superseding is the most
   important thing that ever happens to an entry, so it is the least skippable line.
3. Write the new entry, stating explicitly what the old one got wrong and *why the reasoning
   failed* — not just that it did. Its own `Decided by` is whoever made the *new* call, which
   is frequently not whoever made the old one — and that difference is worth being able to see.

The wrong turn is often the most valuable part of the record. It shows which evidence looked
convincing and was not, which is exactly what stops the same mistake recurring.

A decision that reversed a *correct* earlier belief deserves saying so plainly. "This
reversed a correct earlier belief on bad evidence" is worth more to a future reader than a
tidy history.

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
| **Open** | The question is recorded, the answer is not. Legitimate — better than a fake decision |
| **Superseded by D-NNN** | Wrong or overtaken. Body preserved |

**Open** is not a failure state. Recording "we do not know, here is the fork, here is why it
was not decided today" is more useful than inventing a decision to close the entry.

## Linking a decision to its code

`Implemented by` closes the loop between reasoning and artefact. It answers two questions
nothing else in the repo answers:

- **Was this ever actually built?** An entry that has read *Accepted* for months with no
  implementing commit was either forgotten or never really decided. Both are worth knowing.
- **Did the code drift from the decision?** `git log <sha>..HEAD -- <paths>` shows everything
  that touched the same area afterwards, which is where silent divergence lives.

Add it when the implementing change lands, not when the decision is written — you do not have
the SHA yet, and back-filling a guess is worse than leaving it out. Omit the field entirely
while the status is **Open**.

Same durability caveat as the watermark: SHAs are rewritable by rebase. Keep the date on the
`Status` line so the entry stays locatable even if the hash stops resolving.

## Keeping it honest

- Record the decision **in the same change** that implements it. Reasoning written a week later
  is reconstruction.
- If a decision entry's *premise* turns out wrong, correct the premise and keep the reasoning
  visible — do not quietly rewrite it into correctness.
- Cross-reference: `see D-036` beats restating.
