# The decision log

An append-only record of every non-trivial architectural or scope decision, with its reasoning
and the trade-offs accepted.

Its job is not to record *what* was chosen. Git shows that. Its job is to record **why**, and
**on what evidence**, so a future reader can tell whether the reasoning still holds.

Everything below about **content** — the entry shape, superseding, what earns an entry — holds
regardless of file layout. Layout is a separate choice, and it is not obvious.

## One file, or one file per decision

| | Single file | One file per decision |
|---|---|---|
| Cross-references | Trivial | Need a link or an index |
| Reading the whole history | One open | A directory listing |
| Concurrent writers | **Every entry touches the same append point** | No contention |
| Loading one decision | Pulls in all of them | Just that file |
| Grep by title | Needs grep + scroll | Filename is the title |
| Ceremony | Append and go | New file, frontmatter |

**A single file is right early** — under roughly 30 entries, one writer, and when the whole
log is short enough to read in a sitting. It is genuinely cheaper.

**Split when any of these is true:**

- The file exceeds ~500 lines, or you find yourself reading it with `grep` and line ranges
  instead of opening it — that is the format telling you it has outgrown itself.
- More than one person or agent appends concurrently. Every entry lands at the same place, so
  every pair of concurrent decisions conflicts.
- The log gets loaded into a context window where its size competes with the work.

The split form is the conventional ADR layout: `docs/adr/0042-short-title.md`, one decision
each, status in frontmatter, plus a generated `README.md` index of id / title / status. Keep
the same entry body; only the container changes.

**A note on the numbering pointer below:** a "next id" marker in a shared header is itself a
contention point, and it is the clearest signal that a single file is being asked to do a
directory's job. Under the split layout, the highest filename *is* the pointer.

## Entry format

```markdown
### D-042 — One-line statement of the decision, in the present tense
**Status:** Accepted (2026-08-06). | Open | **SUPERSEDED by D-047 (2026-09-01).**
**Decided by:** gabriel <gabriel@prover.net.br>
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

**`Decided by`** — the person accountable for the choice, captured when the entry is written:

```bash
printf '%s <%s>\n' "$(git config user.name)" "$(git config user.email)"
```

Two things this is **not**:

- **Not the committer.** They diverge — someone lands a decision on another's behalf, or a
  rebase rewrites authorship. Write the name into the entry rather than relying on
  `git log` to reconstruct it, because the file will be rewritten by every later amendment
  and `git blame` on an append-only log points at whoever touched the line last.
- **Not the agent.** In an agent-assisted repo the agent proposes and the human accepts, so
  the git identity is the right one. An entry attributed to a tool records nobody accountable,
  and the point of the field is knowing **who to ask**.

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

Sequential `D-NNN` (or `NNNN-` filenames), never reused.

Under a single file, keep a `next id:` pointer in the header and bump it in the same commit.
Under the split layout, drop the pointer — the highest filename already is it, and one fewer
shared line is one fewer conflict.

## Superseding, never deleting

When an entry turns out to be wrong:

1. Mark the old one **SUPERSEDED by D-NNN**, in place, with a one-line summary of what was
   wrong. Leave the body intact.
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
