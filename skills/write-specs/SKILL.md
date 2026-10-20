---
name: write-specs
description: >
  Use when an idea that is already shaped — a feature description, or the notes and conversation
  of a brainstorm that has ended — is to become spec rules with IDs, product decisions, decision
  entries, open questions and a new milestone in the build order, drafted first and written only
  after the developer says yes. Triggers on: "write the specs for saved jobs", "turn this
  brainstorm into specs", "spec this feature: users can save a job…", "we're done brainstorming,
  write it up as specs", "start the specs for this new project". Not for brainstorming itself (never
  start it or interrupt it), not for building a milestone whose specs exist (implement), and not
  for fixing a bug (fix-bug).
---

# Write specs

Turn a shaped idea into rules `implement` can build from. **Draft, show, wait for the yes, then
write.** Nothing goes into the project before the developer has seen the draft and approved it.

Scripts run as `<python> "${CLAUDE_PLUGIN_ROOT}/skills/<skill>/scripts/<name>.py"`, where
`<python>` is `py -3` on Windows and `python3` elsewhere. Execute them; do not redo by hand what
they do.

## 0. Before starting

- **Brainstorming is not this skill's.** If the developer is still exploring, don't start, and
  never interrupt a brainstorm to talk about specs. Begin when they say it is over; then take all of
  it in one go.
- **The project is the repository the session runs in** (`git rev-parse --show-toplevel`). Not in
  a repository → ask the developer which project, and where it is; never pick one by searching
  folders, even when only one candidate fits. A brand-new project starts only where the developer
  says.
- **Siblings** (`siblings` in `.claude/devflow.json`) are part of the project: a feature whose rules
  any sibling builds is written, under the same yes, into that sibling too — the same spec files,
  product decisions, open questions and milestone, at the folders its own `devflow.json` names — so
  a session opened there starts from them without a second brainstorm (D-041). Decision entries
  are numbered by each repository's own scripts. A sibling not on its default branch with a clean
  working tree → stop and tell the developer before writing anything.
- Read what exists: the specs folder (`specs_dir` in `.claude/devflow.json`, else `docs/specs`) and
  its README, `docs/product/product-decisions.md`, `docs/product/open-questions.md`, the
  `docs/decisions/` index, and the build order (`build_order`, else `docs/product/blueprint.html`,
  section "Build order"). Run `write-specs/scripts/spec_lint.py`; report what it finds before adding
  to it.
- No specs yet and no code → a new project. Code but no specs → a new project's layout, seeded from
  what the code shows; ask before assuming anything it does not show.

## 1. Draft — in the conversation, nothing written yet

**New feature:**
- New rules in the area file the feature belongs to, or a new area file if none fits. Format,
  tags and the README come from [`references/specs-layout.md`](references/specs-layout.md).
- **New IDs only.** The next number after the highest the area has ever used, deleted ones
  included (`git log -p -- <specs_dir> | grep '^-### <AREA>-'`). Never reuse or renumber.
- A new milestone in the build order, naming its rules.

**New project:** the whole layout in `references/specs-layout.md` — `design-system/` and `design/`
only if the input has designs. The first milestone is repository setup.

**Sort what the input decided:**

| What the input produced | Where it goes |
|---|---|
| An answer the developer gave about the product | a line in `product-decisions.md`, and the rules it implies |
| A choice between real alternatives, with reasons | a decision entry, and the rules it implies (they cite it: `see D-012`) |
| A question nobody answered | a line in `open-questions.md`, and a question at the approval step |

- **Never fill a gap.** What the input does not decide stays a question. A fact about the outside
  world you are not sure of → `[VERIFY]`. A rule the AI has no way to test → `[MANUAL]`. Never write
  `[MVP]`: an untagged rule is built.
- **Nothing is accepted by silence.** Every product decision and decision entry you derived rather
  than read from the developer's own words is shown as *proposed*.
- Decision entries follow the evidence skill's log:
  [`${CLAUDE_PLUGIN_ROOT}/skills/evidence-based-decisions/references/decision-log.md`](../evidence-based-decisions/references/decision-log.md).
  Never restate its format here.

## 2. Approval — one step, everything at once

Show, compactly: per spec file, the rules (`ID · title [tag]`); the milestone; the product
decisions and decision entries, each marked as the developer's or proposed; the open questions,
**asked together** as questions. On a project without `docs/decisions/` or `docs/product/`, say
these folders will be created — one approval covers them.

Wait. Answers become product decisions (or entries); requested changes → redraft and show again.
A question still unanswered after the yes stays in `open-questions.md` with what it blocks; a rule
that depends on it is tagged `[VERIFY]` until it is answered.

## 3. Write — only after the yes

**Write what was approved, exactly.** If the answers change the draft — a new rule, a split, a
renumbering, a different tag — show what changed against the approved draft and ask again before
writing: the yes covered the draft as it stood.

1. Spec files, the specs README's file table, the build order.
2. `product-decisions.md` and `open-questions.md` (formats in `references/specs-layout.md`). An
   answered question's line moves from open questions to product decisions.
3. Each decision entry with `evidence-based-decisions/scripts/decision_new.py` (it writes
   `Proposed`); set `Accepted` on the ones the developer confirmed; then `decision_index.py`.
4. Designs: the developer names the artifact ("the design system", "the job list screen").
   Find it among the artifacts their account can open (the Artifact tool's `list`), read it, and
   save its files under `docs/product/design-system/` (a Design System) or `docs/product/design/`
   (a Design, one folder per screen or flow). The copy is the source of truth. More than one match,
   or none listed (shared from another organisation) → ask for the link.
5. `spec_lint.py` passes, in each repository written. Then commit there: `docs(specs): <feature> [<rule IDs>]`. No co-author or
   "generated by" lines.

## 4. Hand over

Tell the developer the milestone is ready, and that `implement` plans and builds it.

## Rules

- The specs folder is the source of truth: if code and a spec disagree, the spec wins or is
  changed first.
- To change behaviour: spec (a new or changed ID) → test → code. Never the other way round.
- Never write before the yes, and never commit what `spec_lint.py` rejects.
- Never push.
