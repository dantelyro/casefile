# 0.16.0 — `write-specs`, the decision-log scripts and `spec_lint` — implementation plan

**Spec:** `docs/specs/2026-10-14-write-specs-design.md` (approved 2026-10-14).
**Starts from:** `c00c9af` on `main`, version `0.15.0` (unpushed).
**Ships as:** `0.16.0`.

**Goal:** a skill that turns a feature description or a finished brainstorm into Inverso-style specs,
product decisions, decision entries, open questions and a new milestone — drafted, shown, and written
only after the developer's yes. The mechanical parts — decision numbering, entries, the index, and
checking the specs hold together — are scripts.

**How this plan is run:** as 0.15.0's: task by task, test first, each committed when green (the
developer's standing instruction, 2026-10-15). Task 7, the live test, needs the developer: the spec
asks for a real brainstorm for an Inverso feature.

## Global constraints

Standard library only, Python ≥ 3.10, `unittest`, each rule tested both ways and mutation-checked,
conventional commits, each rule stated once, nothing written into a project that has not agreed to
it.

## Files

| Path | Task | What |
|---|---|---|
| `skills/evidence-based-decisions/scripts/decision_next_id.py` | 1 | The next free decision id |
| `skills/evidence-based-decisions/scripts/decision_new.py` | 1 | One entry from its fields, `Status: Proposed` |
| `skills/evidence-based-decisions/scripts/decision_index.py` | 1 | `docs/decisions/README.md` regenerated from the entries |
| `skills/evidence-based-decisions/SKILL.md`, `references/decision-log.md` | 2 | Use the scripts; `Proposed` status |
| `skills/write-specs/scripts/spec_lint.py` | 3 | The specs hold together |
| `skills/write-specs/SKILL.md`, `references/` | 4 | The skill and the templates it writes |
| `evals/write-specs-*`, `evals/not-write-specs-*` | 4 | Trigger evals |
| `skills/implement/SKILL.md` | 5 | `spec_lint.py` before planning |
| `docs/decisions/…`, docs, manifests | 6 | Decisions, docs, version |

## Task 1 — The decision-log scripts

- [x] Tests first, in a temporary repository:
  - `decision_next_id.py [dir]`: `D-001` on an empty or missing folder; one past the highest
    `NNNN-` filename; letter-suffixed files (`0013b-…`) never raise the number; `README.md` and
    other files ignored.
  - `decision_new.py --title … --context … --options … --decision … --trade-offs … --decided-by …`:
    writes `NNNN-<slug>.md`, slug from the title's first eight words, lower case, punctuation
    dropped; opens with `# D-NNN — Title`; `**Status:** Proposed (<today>).`; the fields in the
    log's order; `Implemented by` left out; refuses to overwrite; prints the path.
  - `decision_index.py [dir]`: rebuilds the `| Id | Title | Status |` table from the entries' first
    line and `Status` line (bold and date dropped: `Accepted`, `Proposed`, `Open`, `SUPERSEDED by
    D-028`), sorted by filename; keeps the text before and after the table; a folder with no README
    gets one with a short header; `--check` exits 1 when the README differs, writing nothing.
  - On devflow's own log, `decision_index.py --check` passes after one regeneration, and the diff of
    that regeneration is only the hand-written status notes (`Accepted, supersedes D-005`).

## Task 2 — The evidence skill uses the scripts

- [x] `SKILL.md` and `references/decision-log.md`: numbering, a new entry and the index come from the
      scripts, never by hand; `Proposed` joins the status table (written by `write-specs`, becomes
      `Accepted` at the developer's yes, then the index is regenerated).

## Task 3 — `spec_lint.py`

- [x] Tests first, on an Inverso-shaped specs folder:
  - every heading `### <ID> …` parses as `### <ID> · <Title>  [TAG]`; a malformed one is an error
    naming file and line; other `###` headings are ignored;
  - IDs unique across files;
  - every tag is `MVP`, `LATER`, `VERIFY` or `MANUAL`;
  - every rule ID named in the build order's section exists (`build_order` config, default
    `docs/product/blueprint.html`, section "Build order"); a missing build order is reported, not
    an error, for a project that has none yet;
  - every link and every `D-NNN` or rule ID in `docs/product/product-decisions.md` reaches a file,
    an entry or a rule that exists;
  - the specs README's file table lists exactly the `.md` files in the folder (README aside);
  - `--json` output; exit 1 on any error.
- [x] Run it on Inverso's real specs; anything it reports is checked by hand before calling it a
      false positive. Done: 143 rules, no errors; it first flagged `[MVP][VERIFY]` headings, so a
      rule may carry several tags.

## Task 4 — The `write-specs` skill

- [x] `SKILL.md`: read the input → draft → one approval step → write and commit → hand over to
      `implement`. Brainstorming is never interrupted or started by it. Open questions collected and
      asked together. Nothing accepted by silence. Product decisions, logged decisions and open
      questions kept apart per the spec's table. Designs found by name among the developer's
      artifacts and copied into `docs/product/`; more than one match or none listed → ask for the
      link. `spec_lint.py` runs before the commit.
- [x] `references/`: the specs README template (the five rules, the rule format, the tags, the file
      table), and the formats of `product-decisions.md` and `open-questions.md`.
- [x] Trigger evals: a feature description, a finished brainstorm; not a request to brainstorm, not
      "build M2". Not yet run: the account hit its weekly limit (2026-10-16).

## Task 5 — `implement` lints the specs first

- [x] A precondition: `spec_lint.py` passes before planning; its errors are shown and the milestone
      waits for the specs to be fixed.

## Task 6 — Decisions, docs, version

- [x] Decision entries for the choices this release makes; README, CLAUDE.md, manifests, version
      `0.16.0`. Done: D-037 to D-039, written with `decision_new.py`; shipped in `025a2b2`.

## Task 7 — Live test on Inverso (needs the developer)

The spec's test: the output of a real brainstorm for an Inverso feature becomes specs and a
milestone that `implement` builds without inventing a spec gap.
