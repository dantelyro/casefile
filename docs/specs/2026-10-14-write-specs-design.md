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
first); `docs/product/product-decisions.md` records what the developer settled about the product;
`docs/decisions/` records choices between real alternatives, why, and who made them;
`docs/product/open-questions.md` records what is still unanswered and what it blocks. The coverage check in step 4 is `rules_coverage.py` (0.15.0 spec), standard library only.

## The layout (Inverso's, as the default)

```
docs/
  product/
    blueprint.html          the project at a glance; its "Build order" section lists the milestones
    product-decisions.md    what the developer settled about the product, one line each
    open-questions.md       what still needs an answer: question, what it blocks, who answers
    design-system/          colours, type, spacing, components: a copy of a Design System artifact
    design/                 the screens: a copy of each Design artifact
  decisions/                the evidence skill's decision log: choices between real alternatives
    README.md               its index (id, title, status)
    NNNN-kebab-slug.md      one decision per file
  specs/
    README.md               how the project works with specs, the rule format, the tags, the file table
    01-…, 02-…, 03-…        foundations: product, architecture, data model
    10-… to 2x-…            one file per area (auth, matching, jobs, …), plus testing and deploy
```

### Product decisions and logged decisions are two different things

Inverso kept `docs/specs/00-decisions.md`, one line each with ✅ / 🔵 / 🟡. Most of its lines are not
decisions in the evidence skill's sense: they are the owner's answers about the product ("Brazil
first", "the top 20 matches are free") — no alternatives weighed, no evidence to grade. They are
requirements stated by the person who owns them. A few lines are real choices between alternatives.
`write-specs` keeps the two apart:

| What the brainstorm produced | Where it goes |
|---|---|
| An answer the developer gave about the product | a line in `docs/product/product-decisions.md`, and the spec rules it implies |
| A choice between real alternatives, with reasons | an entry in `docs/decisions/`, in the evidence skill's format, and the spec rules it implies |
| A question nobody answered | a line in `docs/product/open-questions.md` |

- **`product-decisions.md`**: one line per answer — the answer, its date, and links to the spec rules it
  produced. The reasoning, if any, is in the rule or the decision entry, never restated here (D-008).
  When an open question is answered, its line moves from `open-questions.md` to `product-decisions.md`.
- **Nothing is accepted by silence.** Inverso's 🔵 "proposed by Claude, accepted unless changed" read as
  decided. A line or entry the developer has not confirmed is shown as proposed in the draft, and is
  written only after the approval step. Decision entries are written `Status: Proposed` and become
  `Accepted` at that step.
- A spec rule that exists because of a logged decision cites it (`see D-012`); the reasoning stays in
  the entry.

Inverso's existing `00-decisions.md` is split separately, with the developer's agreement — answers to
`docs/product/product-decisions.md`, real choices to reconstructed entries via the evidence skill's
seeding procedure. Not part of this release.

### Designs

Designs are made as claude.ai artifacts — in the Claude app or from the terminal — and the project keeps
a copy, because a link can change or disappear without the project noticing. The copy is the source of
truth; the artifact is a viewer of it (Inverso's `docs/design/USING.md`).

| Artifact type | Copied to | What it is |
|---|---|---|
| Design System | `docs/product/design-system/` | tokens, brand book, components |
| Design | `docs/product/design/` | screens and mockups, one artifact per screen or flow |

- **No link needed.** The developer names the artifact ("the Inverso design system", "the job list
  screen") and `write-specs` finds it in the artifacts the logged-in account can open. A name that
  matches more than one, or an artifact shared from another organization (not listed), → ask for the
  link.
- **Folders are created after the developer agrees**, at the approval step, and only for the kinds of
  design the input has.
- Spec rules for a screen link the screen's file under `design/`; component rules link the component
  under `design-system/`.
- A new screen designed during specs uses the project's design system, so it uses the same tokens the
  code is held to.

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

**Milestones** live in `docs/product/blueprint.html`, section "Build order": each milestone a slice that runs
end to end, in order, with what it covers. A feature added to an existing project becomes a new
milestone there.

## The flow

1. **Read the input**: the feature description, or the brainstorm's output, plus the existing specs
   if the project has them.
2. **Draft**:
   - New project → the whole layout above (`design-system/` and `design/` only if the input has them). The first milestone is repository setup.
   - New feature → new rules in the area file it belongs to (new IDs; IDs are never reused or
     renumbered), a new area file if none fits, a new milestone in the build order, and each decision
     the feature makes sorted per the table above.
   - Anything the input does not decide → a line in `open-questions.md` and a question to the
     developer. Never filled in. Unsure facts about the outside world → `[VERIFY]`, never `[MVP]`.
3. **Ask for approval**: show the draft — rule list per file, the milestone, the product decisions
   and decision entries, the open questions — and
   wait. Changes requested → redraft. Only after a yes are the files written and committed.
4. **Hand over**: `implement` can now plan the new milestone.

## Scripted steps

| Script | Checks |
|---|---|
| `spec_lint.py` | every rule heading parses; IDs unique across files; every tag is `MVP`, `LATER`, `VERIFY` or `MANUAL`; every milestone in the build order names rules that exist; every link in `product-decisions.md` reaches a rule or entry that exists; the README file table matches the files |

Standard library only, tested in the 0.13.0 suite, and run by `implement` too before planning.

## Accepted when

`write-specs` turns the output of a real brainstorm for an Inverso feature into specs and a milestone
that `implement` then builds without a spec gap being invented (see *Live test on Inverso* in the
0.13.0 spec).
