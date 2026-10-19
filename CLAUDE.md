# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Docs reconciled through:** `3953145` — 2026-10-19

## What this repo is

A Claude Code plugin marketplace **and** the single plugin it ships, in one repository. There is
no build and no dependencies — the product is Markdown (skills) plus hooks in standard-library
Python, with a `unittest` suite. Changing a file here changes how future Claude Code sessions behave, including sessions in
this repo.

## Commands

```bash
# Register the working copy as a marketplace, to test changes before pushing
/plugin marketplace add C:\Users\beyon\projects\devflow

# Install from GitHub (what users run)
/plugin marketplace add dantelyro/devflow
/plugin install devflow@dantelyro

# Run the test suite (standard library only; use py -3 on Windows)
python -m unittest discover -s tests

# Trigger evals for the skills (billed, so on demand; results/ is gitignored). --scaffold runs each
# case's fixture.sh, which sets up a small repo: in an empty folder runs give up before choosing a skill
claude plugin eval . --ablation none --no-publish --scaffold

# Exercise a hook exactly as Claude Code invokes it, with a captured event
CLAUDE_PLUGIN_ROOT="$PWD" sh hooks/run-hook session_start < tests/fixtures/session_start_startup.json | python -m json.tool
```

**Every shipped change bumps `version` in `.claude-plugin/plugin.json`.** Claude Code refreshes
known marketplaces on startup, so a bump is what makes installed copies pick the change up;
without one, nothing updates. Git history shows the convention: minor for a new skill or hook,
patch for wording.

The plugin `description` is duplicated in `plugin.json` and `marketplace.json` — the only
intentional duplication in the repo. Change both together.

## Architecture

**Root is the plugin.** `marketplace.json` points its one entry at `source: "./"`, so
`.claude-plugin/` holds both manifests side by side rather than nesting the plugin under
`plugins/`. A *second* plugin would therefore need `plugins/<name>/.claude-plugin/plugin.json`
and its own `marketplace.json` entry — the root is taken. See D-002.

**`hooks/hooks.json` is auto-discovered.** No `plugin.json` entry references it. Its command
path is built from `${CLAUDE_PLUGIN_ROOT}`.

**Two-tier skill loading.** `SKILL.md` is loaded in full whenever the skill triggers, so it stays
small and states the principles. Anything long — formats, procedures, tables — lives in
`references/` and is read only when the work needs it. Keep new material on the correct tier;
growing a `SKILL.md` taxes every session that triggers it. See D-001.

**The hook exists because a description cannot match "session start".** A skill fires when the
model recognises its `description` in the situation in front of it. `evidence-based-decisions`
triggers on the *start of a session* and on *facts about the repo*, neither of which any first
user message states. `hooks/devflow_hooks/session_start.py` injects that trigger — as a **pointer to the skill,
not the skill body**, so the per-session cost is a few hundred tokens. Preserve that property.
See D-003 and D-004.

**Six skills and three agents, each with its own moment.** `repo-discovery` reads a project that
already exists; `evidence-based-decisions` records *why* and keeps it honest; `review` dispatches
`devflow:reviewer` for a verdict on one change; `fix-bug` takes one issue from `docs/issues/` through
`devflow:implementer`, the reviewer and a merge; `implement` builds a milestone of spec rules from
a `devflow:planner` plan, task by task through the same implementer, reviewer and merge, and never
writes code, tests or specs itself — the plan file is the progress record (D-034, D-035); a task that conflicts at merge is redone from the default branch (D-036); `write-specs` drafts specs, product decisions, decision entries and a milestone from a feature or a finished brainstorm and writes them only after the developer's yes (D-037, D-039), recording decisions through the evidence skill's scripts (D-038). Instructions more than one skill uses live in
`shared/` and are linked directly from each `SKILL.md` (D-032). None writes a document into
a project that has not agreed to it. Agents live flat in `agents/` (a subfolder becomes part of the
name), and every rule an agent must obey is a plugin hook branching on `agent_type`, because a
plugin agent's own `hooks` and `permissionMode` are ignored (D-030). The two greenfield skills were removed in 0.12.0 (D-026); the
agent workflows that replace them are designed in `docs/specs/history/2026-10-14-*` and land one release at
a time, `write-specs` among them.

**Per-project settings are `.claude/devflow.json`**, read through `hooks/devflow_hooks/lib.py`
(`_DEFAULTS`, `_TYPES`: a new key is added to both). Skills and agents read it, and `review` step 2
is where its contents are proposed: apps with `test`, `install` and optional `lint` (D-042),
`default_branch`, and `repo` with `siblings` for a frontend and backend in separate repositories,
where every repository holds the same specs and plan and builds only its own tasks (D-041). The
planner marks any detail no spec rule states as a `Planner choice:` and the developer rules on each
(D-044).

## Hook gotchas

Each of these is load-bearing; the comments in the files say so too.

- **Every hook goes through one starter:** `sh "${CLAUDE_PLUGIN_ROOT}/hooks/run-hook" <name>`, which
  finds Python 3.10+ and runs `hooks/run.py <name>`, which runs `devflow_hooks/<name>.py`. Claude
  Code runs hook commands through `sh` on macOS/Linux and Git Bash on Windows, so devflow requires
  Git for Windows; under PowerShell the command does not even parse (probe, 0.13.0 spec).
- **Guards fail closed.** `run.py` denies when the hook is unknown, its input is unreadable or it
  crashes, and every guard is registered with `onFailure: "block"`, because Claude Code otherwise
  lets the action through when a hook crashes or times out. `session_start` is the exception: it
  only adds context, so it never blocks.
- **Decisions are JSON on stdout, exit 0** (`permissionDecision`: `deny` or `ask`); printing nothing
  allows. Exit 2 is only the starter's "no Python" path.
- **The starter uses only shell builtins until Python is found**, so it still explains a missing
  Python with an empty `PATH`. It tries `py -3` first: `python3` on Windows can be the Microsoft
  Store stub.
- **Emit exactly one context field.** Claude Code reads both `additionalContext` and
  `hookSpecificOutput.additionalContext` without deduplicating, so `session_start` emits the nested
  form under Claude Code (`CLAUDE_PLUGIN_ROOT` set) and the top-level form elsewhere.
- **Devflow agents get one command per call.** `guard_bash` denies `;`, `&&`, `||`, several lines,
  `| tail` and `sleep`/`until` loops for devflow's own agents (`devflow:*`), so a hung check cannot hide
  inside a chain (D-043).
- **Only the standard library.** A test fails on any import outside `sys.stdlib_module_names`.

## Skill-authoring baseline

What Anthropic documents about skills — loading, frontmatter, references, compaction — is kept in
`docs/skill-authoring.md`, imported here so it is read at every session start:

@docs/skill-authoring.md

That file is watermarked with the Claude Code version it was verified against. **At the start of
every session, run `claude --version` and compare it with the file's `Verified against` line.** If
the running version is newer:

1. Read the changelog entries between the two versions, and re-fetch the pages the file cites.
2. Update `docs/skill-authoring.md` with whatever changed, and move its watermark to the running
   version and today's date — even when nothing changed, so the same range is not checked twice.
3. Check the skills against what changed and tell the user, before starting the session's
   task, about anything that could change how they trigger, load or read their references. Do not
   edit the skills without approval.

The check exists because skill behaviour is set by a CLI that ships several releases a week; a rule
verified once and never re-checked becomes a belief about an old version (D-024).

## Editing skills

- The YAML `description` is the entire trigger surface — it is what the model matches a situation
  against. Editing it changes when the skill fires; editing the body only changes what it then
  does. `name` must match the directory name.
- **Never nest references.** A file under `references/` must not send the reader to another
  reference file — in its own skill or another one. Every reference is linked directly from its
  skill's `SKILL.md`, at the step that needs it. Anthropic documents that a file reached through
  another reference may be previewed with `head -100` instead of read, so a nested reference is a
  rule that can silently go unread (D-024).
- **State each rule once, in the place it applies** (D-008). The skills warn against documents
  that can disagree with each other; the same applies to this repo's own files. If a rule belongs
  in a `references/` file, do not also summarise it in `SKILL.md` or the README.
- Skill prose carries its **reasons**, not just its rules — the "Rationalizations" and "Red flags"
  tables exist because a rule without its reason gets optimised away. Match that register when
  adding to them. **A reason earns its place only if it carries project knowledge the model cannot
  infer** — a failure seen here, a constraint of this repo, a vendor behaviour. Cut prose that
  explains general concepts or repeats a reason already given; Anthropic's guidance is to state what
  to do, not narrate how or why, and every loaded line is a recurring cost (D-024).

## Where the reasoning lives

`docs/decisions/` holds the *why* behind the arrangements above — one file per decision, indexed
in `docs/decisions/README.md`. It was seeded retroactively on 2026-08-27, so every existing entry
is marked as a reconstruction. Record new decisions in the same change that implements them, per
`skills/evidence-based-decisions/references/decision-log.md`.

devflow is specified in its own `write-specs` layout and built with `implement` (D-047): rules with
IDs in `docs/specs/`, the build order in `docs/product/blueprint.md`, milestone plans in
`docs/plans/`. Designs of releases through 0.19.1 are in `docs/specs/history/`.

There is no separate architecture document: at this size the architecture *is* this file, which is
why the reconciliation watermark sits in the header above. Move it in the same commit as any doc
update, so it always names a commit whose docs were true.

This file has to name `docs/decisions/` explicitly. The SessionStart hook injects the *trigger*
for `evidence-based-decisions`; it cannot say where a given project keeps its log, and the skill
cannot know before reading the repo. Project instructions are the only document loaded on every
session, so this pointer is what makes the log findable rather than stumbled upon. It is a
location, not a summary — the reasoning stays in the entries (D-008).

## Commits

**Always use conventional commits** — `feat:`, `fix:`, `docs:`, and the rest of the set. This is
not style. `Decided by` in the decision log is resolved by filtering `git log -L` on the lines a
decision governs down to `feat` and `fix`, because those are the commits that decide something
while `docs`, `chore`, `style`, `test`, `ci` and `build` touch lines without deciding anything.
Drop the prefixes and every future attribution in this repo falls back to reading subject lines
by hand — the degraded path the skill documents for other people's repos. See D-007.

Phrase the subject as the change's intent, not the files touched. Commit bodies are the place for
wrong diagnoses and rejected alternatives — what does not belong in a decision entry.
