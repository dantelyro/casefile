# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

**Docs reconciled through:** `f6e4595` — 2026-10-14

## What this repo is

A Claude Code plugin marketplace **and** the single plugin it ships, in one repository. There is
no build, no test suite and no dependencies — the product is Markdown (skills) plus one shell
hook. Changing a file here changes how future Claude Code sessions behave, including sessions in
this repo.

## Commands

```bash
# Register the working copy as a marketplace, to test changes before pushing
/plugin marketplace add D:\projects\personal\devflow

# Install from GitHub (what users run)
/plugin marketplace add dantelyro/devflow
/plugin install devflow@dantelyro

# Exercise the SessionStart hook exactly as Claude Code invokes it
CLAUDE_PLUGIN_ROOT="$PWD" ./hooks/run-hook.cmd session-start

# Check the JSON it emits is well-formed and contains exactly one context field
CLAUDE_PLUGIN_ROOT="$PWD" ./hooks/run-hook.cmd session-start | python -m json.tool
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
user message states. `hooks/session-start` injects that trigger — as a **pointer to the skill,
not the skill body**, so the per-session cost is a few hundred tokens. Preserve that property.
See D-003 and D-004.

**Two skills, each with its own moment.** `repo-discovery` reads a project that already exists;
`evidence-based-decisions` records *why* and keeps it honest. Neither writes a document into a
project that has not agreed to it. The two greenfield skills were removed in 0.12.0 (D-026); the
agent workflows that replace them are designed in `docs/specs/2026-10-14-*` and land one release at
a time. Until `write-specs` ships, no devflow skill writes a new project's specs or claims `/init`
in an empty directory.

## Hook gotchas

Each of these is load-bearing; the comments in the files say so too.

- **Hook scripts are extensionless on purpose** (`session-start`, not `session-start.sh`). Claude
  Code's Windows auto-detection prepends `bash` to any command containing `.sh`, and the wrapper
  is already choosing the interpreter. See D-005 for this and the two rules below.
- **`run-hook.cmd` is a cmd/bash polyglot.** The leading `: << 'CMDBLOCK'` line makes the batch
  section a no-op heredoc under bash; cmd.exe ignores the trailing shell lines. Do not reorder
  the file or add anything above that first line.
- **When no bash is found, the wrapper exits 0 silently.** A genuinely broken hook therefore looks
  exactly like a machine without bash — the right trade for optional context, the wrong one for
  anything load-bearing.
- **The `directive` string in `session-start` is spliced into a `printf` JSON template verbatim,
  with no escaping pass.** It must contain no double quotes, backslashes or single quotes. `\n`
  sequences stay literal in the shell and become real newlines when the JSON is parsed.
- **Emit exactly one context field.** Claude Code reads both `additionalContext` and
  `hookSpecificOutput.additionalContext` without deduplicating, so the script branches on
  `CLAUDE_PLUGIN_ROOT` and emits the nested form under Claude Code, the top-level form elsewhere.

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
