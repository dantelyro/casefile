# `write-specs` — from a feature description or brainstorm to milestone specs — design

**Date:** 2026-10-14.
**Status:** Approved 2026-10-14. Not yet implemented.
**Release:** `0.16.0`. Needs `0.13.0` (hook runtime and tests) and `evidence-based-decisions` (it
writes decisions through that skill's log and scripts). Produces what `implement` (0.15.0) reads.

## Summary

`write-specs` turns an idea that is already shaped into rules `implement` can build from, laid out
the way Inverso's are. It **drafts, then asks for approval**: nothing is written into the project
until the developer has seen the draft and said yes.

| Input | Example |
|---|---|
| A feature description | "Users can save a job and see saved jobs on a page" |
| The output of a brainstorming session | Inverso's specs and blueprint came from one |

**Brainstorming itself is not part of this skill, or of any devflow skill.** It stays free and
unconstrained, and is never interrupted to talk about specs. Its output is rough — notes and
conversation — and `write-specs` turns all of it into specs **in one go, after the brainstorm ends**.
Questions the brainstorm left open are collected and asked together at the approval step, not along
the way.

## The rules carried over from Inverso

Every project specced with `write-specs` gets Inverso's rules, written into its `docs/specs/README.md`:

1. **Spec first.** Every feature has a file. Each rule has an ID (`MATCH-003`).
2. **Test second.** Before any code, a failing test whose name starts with the rule ID
   (`it("MATCH-003: …")`, `def test_MATCH_003_…`).
3. **Code third.** The least code that makes it pass, then refactor.
4. **Trace.** A coverage check lists every rule ID with no test; CI fails if an `[MVP]` rule has none.
5. **Change.** To change behaviour: spec (new or changed ID) → test → code. Never the other way round.

Plus: the specs folder is the source of truth (if code and spec disagree, the spec wins or is changed
first); `docs/decisions/` records every decision, why, and who made it; `99-open-questions.md` records
what blocks what. The coverage check in step 4 is `rules_coverage.py` (0.15.0 spec), standard library only.

## The layout (Inverso's, as the default)

```
docs/
  blueprint.html            the project at a glance; its "Build order" section lists the milestones
  decisions/                the evidence skill's decision log — the only record of decisions
    README.md               its index (id, title, status)
    NNNN-kebab-slug.md      one decision per file
  specs/
    README.md               how the project works with specs, the rule format, the tags, the file table
    01-…, 02-…, 03-…        foundations: product, architecture, data model
    10-… to 2x-…            one file per area (auth, matching, jobs, …), plus testing and deploy
    99-open-questions.md    what still needs an answer: question, what it blocks, who answers
```

### Decisions blend with the evidence skill

Inverso kept its decisions in `docs/specs/00-decisions.md`, one line each with ✅ / 🔵 / 🟡. It never
used `evidence-based-decisions`, and that format breaks three of its rules: one file for every
decision, "proposed by Claude, accepted unless changed" reading as decided, and a second decision
record beside `docs/decisions/` if the evidence skill ever ran. So `write-specs` does **not** create
`00-decisions.md`:

- Every decision a brainstorm or feature makes becomes an entry in `docs/decisions/`, in the evidence
  skill's format (`skills/evidence-based-decisions/references/decision-log.md`, linked directly from
  `write-specs`'s `SKILL.md`): context, options, decision, trade-offs, evidence grade, status,
  `Decided by`.
- A decision the developer has not confirmed is written `Status: Proposed`, and becomes `Accepted` only
  at the approval step. Nothing is accepted by silence.
- The quick glance `00-decisions.md` gave is the log's own index, `docs/decisions/README.md`; the specs
  README's file table links to it in that row. No second index.
- A spec rule that exists because of a decision cites it (`see D-012`); the reasoning stays in the
  entry, never restated in the spec (D-008).

Inverso's existing `00-decisions.md` is converted separately, with the developer's agreement, as
reconstructed entries — the evidence skill's existing seeding procedure. Not part of this release.

### Working with `evidence-based-decisions`

The evidence skill **owns** the decision log; `write-specs` **uses** it:

- **Format and attribution** stay in `evidence-based-decisions/references/decision-log.md`, linked
  directly from `write-specs`'s `SKILL.md`. Never restated.
- **The mechanical parts are scripts** in `skills/evidence-based-decisions/scripts/`, executed by both
  skills, standard library only, tested in the 0.13.0 suite:

  | Script | Does |
  |---|---|
  | `decision_next_id.py` | the next free id from the highest filename, letter suffixes included |
  | `decision_new.py` | writes one entry from its fields, in the log's format, with `Status: Proposed` |
  | `decision_index.py` | regenerates `docs/decisions/README.md` from the entries |

  Whoever writes an entry, the numbering and the index come out the same — the inconsistency seen
  with the evidence skill comes from leaving these steps to judgement.
- **One approval, not two.** On a project without `docs/decisions/`, the evidence skill would propose
  its doc set and ask; `write-specs` folds "create `docs/decisions/`" into its own approval step, so the
  developer is asked once.
- **Reconciliation stays with the evidence skill.** Specs are context documents like any other; the
  evidence skill's watermark replay covers `docs/specs/` and `docs/decisions/` at session start.

Rule format, from Inverso's `docs/specs/README.md`:

```
### MATCH-003 · Required skills weigh 70%            [MVP]
Given a job with required and nice-to-have skills
When the score is computed
Then required skills contribute 70 of the 100 points
```

Tags: `[MVP]` must ship · `[LATER]` planned, not built yet · `[VERIFY]` depends on an outside fact to
confirm before building · `[MANUAL]` cannot be tested automatically; checked in review or a release
checklist.

**Milestones** live in `docs/blueprint.html`, section "Build order": each milestone a slice that runs
end to end, in order, with what it covers. A feature added to an existing project becomes a new
milestone there.

## The flow

1. **Read the input**: the feature description, or the brainstorm's output, plus the existing specs
   if the project has them.
2. **Draft**:
   - New project → the whole layout above. The first milestone is repository setup.
   - New feature → new rules in the area file it belongs to (new IDs; IDs are never reused or
     renumbered), a new area file if none fits, a new milestone in the build order, and a
     `Proposed` decision entry for each decision the feature makes.
   - Anything the input does not decide → a line in `99-open-questions.md` and a question to the
     developer. Never filled in. Unsure facts about the outside world → `[VERIFY]`, never `[MVP]`.
3. **Ask for approval**: show the draft — rule list per file, the milestone, the proposed decisions,
   the open questions — and
   wait. Changes requested → redraft. Only after a yes are the files written and committed.
4. **Hand over**: `implement` can now plan the new milestone.

## Scripted steps

| Script | Checks |
|---|---|
| `spec_lint.py` | every rule heading parses; IDs unique across files; every tag is `MVP`, `LATER`, `VERIFY` or `MANUAL`; every milestone in the build order names rules that exist; the README file table matches the files |

Standard library only, tested in the 0.13.0 suite, and run by `implement` too before planning.

## Accepted when

`write-specs` turns the output of a real brainstorm for an Inverso feature into specs and a milestone
that `implement` then builds without a spec gap being invented (see *Live test on Inverso* in the
0.13.0 spec).
