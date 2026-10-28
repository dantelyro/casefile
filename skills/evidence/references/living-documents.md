# Living documents

The small set of files that are the project's source of truth, and the discipline that keeps them
true.

## Contents
- The set
- Purpose
- The architecture overview
- What belongs in project instructions
- Correcting a false claim
- The watermark: knowing what changed while you were away
- Keeping status current
- Commit messages as the third record

## The set

| File | Answers | Read it |
|---|---|---|
| Project instructions (`CLAUDE.md`, `AGENTS.md`) | How to run, build, test; the gotchas that cost real time | Always — it is loaded for you |
| Purpose (`docs/purpose.md`) | What pain this solves, for whom, and what it deliberately is not | Before scoping anything, and whenever a request seems out of scope |
| Architecture overview (`docs/architecture/overview.md`) | How the code is organised, which patterns it follows and how faithfully, the conventions to copy, per-module state | Before designing or building anything |
| Decision log | Why it is this way, and what was given up | Scan for entries your approach would contradict |
| Roadmap / phase spec | What to build next, and in what order | Before picking up work |
| Captured external specs | What the third-party system actually accepts | Before the vendor's prose |

Keep them **non-overlapping**: the instructions file points at the architecture document rather
than restating it. Duplication is what lets two files disagree.

## Purpose

The core: the pain, who has it, what this does about it, and — the half that gets skipped — what
it deliberately does **not** do. A purpose document with no non-goals cannot settle an argument,
which is the only reason to have one.

Short, and stable. It changes rarely; when it does, that is a decision and gets an entry.

## The architecture overview

What someone about to add code needs: where it goes, what shape to give it, and what to distrust.
A list of what exists and where answers none of that. The watermark sits in its header (see "The
watermark" below). Then these sections, in this order; omit one the project has nothing for (a
CLI has no request flow) rather than filling it:

1. **One sentence** — the architectural style and main patterns, named: "layered Express API with
   repository pattern over Prisma and async jobs on BullMQ".
2. **Folder structure** — a tree of the source folders, one comment per entry saying what goes
   there. Mark generated folders as never-edit. Stop at folder level unless a single file is a
   structural piece (composition root, bootstrap, auth hook).
3. **Patterns** — a table of the patterns the code uses: Pattern · Where / evidence · Caveats.
   Evidence is a path or a symbol. Caveats say how faithfully it is applied: "the repository
   interfaces use ORM types".
4. **SOLID check** — one row per principle, a verdict (✅ / 🟡 / ❌) and the evidence. A verdict
   without a file or class behind it does not go in.
5. **Request flow** — one numbered walkthrough per main use case, from the entry point to the side
   effects, async boundaries marked, then the error mapping (which exception becomes which status).
6. **Conventions** — a Topic · Convention table: file naming, imports, how to add an endpoint,
   repository, dependency or job; then DB naming, auth, lint, tests, commits, branches. Each row is
   a recipe someone can follow without asking.
7. **Module state** — built, verified, stub or table-only, per "Keeping status current".
8. **Known gaps** — defects and risks in code that exists, each read from the code and dated.
9. **Environments** — branch → URL → deploy mechanism.

Rules:

- **Only state what exists.** No "DDD: no", "CQRS: none", "no event bus". An absence goes in only
  as a gap in existing code (section 8), never as a pattern verdict.
- **Name things by their real kind.** Queue jobs that are commands with one consumer each are a
  "job queue (commands)", not "event-driven".
- **Every claim points at code** — a path, class or config key. Prose that cannot be traced to the
  repo belongs in `purpose.md` or nowhere.
- **No why, no run commands.** Reasons live in the decision log, linked as D-NNN; how to run and
  test lives in the project instructions, which point here for structure and conventions.

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

**Record the commit each reconciliation was made through**, in the architecture document's header:

```markdown
**Docs reconciled through:** `fda5e88` — 2026-08-06
```

Where there is no architecture document — a repo small enough that the project instructions *are*
the architecture — put it in the project instructions header instead, and point the `grep` at that
file. Exactly one location per repo: a watermark in two files is two watermarks, and the stale one
is the one that gets read.

At session start, diff the gap:

```bash
DOC=docs/architecture/overview.md       # or the project instructions, if that is where it lives
WM=$(sed -n 's/.*reconciled through:[^`]*`\([0-9a-f]\{7,40\}\)`.*/\1/p' "$DOC" | head -1)

if [ -z "$WM" ]; then
  echo "no watermark in $DOC — do not read this as up to date"
elif git cat-file -e "$WM^{commit}" 2>/dev/null; then
  git diff --stat "$WM"..HEAD -- src/ migrations/
else
  echo "watermark $WM no longer resolves — see recovery below"
fi
```

**Check for the empty case before diffing.** `git diff ..HEAD` with an empty left side is not an
error — both sides default to `HEAD`, so it prints nothing, and nothing is exactly what an
up-to-date repo prints. A failed extraction is indistinguishable from a clean reconciliation
unless you test for it. POSIX `sed` rather than `grep -oP` for the same reason: `-P` is a GNU
extension, and on Git Bash under a non-UTF-8 locale it exits with *"-P supports only unibyte and
UTF-8 locales"* — straight into the silent-empty path.

Scope the paths to source. A doc-only commit did not change the system, and including it means
every reconciliation reports work that needs reviewing.

Diff rather than replay the log: a change that was made and then reverted cancels out in the
diff, while `git log` lists both commits as work to review. Run `git log -- <file>` on a changed
file only when you need to know why it changed.

Read what comes back, update whatever it invalidated, then move the watermark **in the same
commit** as the doc update — so the watermark always names a commit whose docs were true.

### When it breaks

| Symptom | Cause | Recovery |
|---|---|---|
| SHA does not resolve | Rebase, squash, amend, force-push | Fall back to the date beside it: `git diff --stat "$(git rev-list -1 --before=2026-08-06 HEAD)"..HEAD -- src/` |
| Shallow clone | `--depth` fetch | `git fetch --unshallow`, or use the date |
| Huge range on first run | Watermark never set | Set it to `HEAD`, note that the docs are unverified before that point, and reconcile from now on |

Keep the **date** next to the SHA precisely because SHAs are rewritable and dates are not. The SHA
is exact when it works; the date always works and is approximately right.

Decision entries carry the same link in the other direction — `Implemented by`, and the same date
caveat.

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
