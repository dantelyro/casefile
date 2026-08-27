# Living documents

The small set of files that are the project's source of truth, and the discipline that keeps them
true.

## The set

| File | Answers | Read it |
|---|---|---|
| Project instructions (`CLAUDE.md`, `AGENTS.md`) | How to run, build, test; the gotchas that cost real time | Always — it is loaded for you |
| Architecture / mental model | What exists, where it lives, module boundaries, per-module state | Before designing or building anything |
| Decision log | Why it is this way, and what was given up | Scan for entries your approach would contradict |
| Roadmap / phase spec | What to build next, and in what order | Before picking up work |
| Captured external specs | What the third-party system actually accepts | Before the vendor's prose |

Keep them **non-overlapping**: the instructions file points at the architecture document rather
than restating it. Duplication is what lets two files disagree.

## What belongs in project instructions

The gotchas — each one a bug that already cost hours:

- A config value whose absence crashes the process rather than the request
- A framework setting required on every instance, and what breaks without it
- The one spec file to copy when writing a new one of its kind
- Rules with teeth, and *why*: "never call production — a production call issues a real fiscal
  document"
- Corrections to prior beliefs, stated as corrections

Write the **why**, not just the rule. A rule without its reason gets optimised away by the next
person who finds it inconvenient.

## Correcting a false claim

When a document says something now known to be false, fix it **immediately**, as its own concern
— not bundled into whatever task revealed it, and not deferred for approval. A known-false
document is worse than a missing one: it is read confidently by someone without your context.

**Then sweep.** One wrong belief is rarely recorded once. Grep the corrected claim across every
living document, source comment, and test comment; in practice a single correction lands in four
to six places.

**Preserve the trail** with a supersession banner rather than a silent rewrite:

```markdown
> **Partly corrected on 2026-08-05 — read §8e alongside this.** Its central conclusion holds:
> …. Three details here are wrong: …. Kept intact as the trail.
```

Be precise about scope. "Substantially superseded" when only three details were wrong sends
readers away from a section that is mostly right.

Historical records — completed plans, past task reports — are **not** living documents. Leave them
as they were; correct only what is presented as currently true.

## The watermark: knowing what changed while you were away

Docs describe the code as of the last reconciliation, not as of now. People commit without an
agent, so the gap is real and invisible unless you record where you stopped.

**Record the commit each reconciliation was made through**, in the architecture document's header:

```markdown
**Docs reconciled through:** `fda5e88` — 2026-08-06
```

At session start, replay the gap:

```bash
DOC=docs/architecture/mental-model.md   # or the project instructions, if that is where it lives
WM=$(sed -n 's/.*reconciled through:[^`]*`\([0-9a-f]\{7,40\}\)`.*/\1/p' "$DOC" | head -1)

if [ -z "$WM" ]; then
  echo "no watermark in $DOC — do not read this as up to date"
elif git cat-file -e "$WM^{commit}" 2>/dev/null; then
  git log --oneline "$WM"..HEAD -- src/ migrations/
else
  echo "watermark $WM no longer resolves — see recovery below"
fi
```

**Check for the empty case before replaying.** `git log ..HEAD` with an empty left side is not an
error — both sides default to `HEAD`, so it prints nothing, and nothing is exactly what an
up-to-date repo prints. A failed extraction is indistinguishable from a clean reconciliation
unless you test for it. POSIX `sed` rather than `grep -oP` for the same reason: `-P` is a GNU
extension, and on Git Bash under a non-UTF-8 locale it exits with *"-P supports only unibyte and
UTF-8 locales"* — straight into the silent-empty path.

Scope the paths to source. A doc-only commit did not change the system, and including it means
every reconciliation reports work that needs reviewing.

Read what comes back, update whatever it invalidated, then move the watermark **in the same
commit** as the doc update — so the watermark always names a commit whose docs were true.

### When it breaks

| Symptom | Cause | Recovery |
|---|---|---|
| SHA does not resolve | Rebase, squash, amend, force-push | Fall back to the date beside it: `git log --since=2026-08-06 --oneline -- src/` |
| Shallow clone | `--depth` fetch | `git fetch --unshallow`, or use the date |
| Huge range on first run | Watermark never set | Set it to `HEAD`, note that the docs are unverified before that point, and reconcile from now on |

Keep the **date** next to the SHA precisely because SHAs are rewritable and dates are not. The SHA
is exact when it works; the date always works and is approximately right.

Decision entries carry the same link in the other direction — `Implemented by`, and the same date
caveat. See "Linking a decision to its code" in `decision-log.md`.

## Keeping status current

The architecture document's per-module table drifts fastest and misleads most. Update it in the
same change that alters module state, and encode the distinction that matters:

```markdown
| `events`   | cancelamento + manifestação via Sefin; consult via ADN | ✅ built  |
| `billing`  | subscription gating                                    | ⬜ stub   |
```

Where "built" and "verified against the real system" differ for a module, say which. A table
reading ✅ for something never exercised against production is the same false confidence in a
smaller font.

## Commit messages as the third record

Docs hold the current truth; commits hold the reasoning at a moment. Use them for what does not
belong in a decision entry:

- The two diagnoses that were wrong, and how each was ruled out
- What a test proved and what it could not
- Why an alternative was rejected as unpromising

Writing "wrong 1 / wrong 2 / actual" into a commit is what stops the next person re-walking both
dead ends. It costs a paragraph.
