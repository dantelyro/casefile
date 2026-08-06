---
name: context-updater
description: >
  Automatically update codebase context documents after any meaningful code change, or before starting any changes.
  ALWAYS trigger this skill at start of a session or the end of any task that involves: creating, editing, deleting,
  or refactoring source files; adding or removing dependencies; changing configuration files;
  adding new modules, services, routes, entities, or components; running migrations; or
  restructuring the project. This includes bugfixes, new features, refactors, and dependency
  updates. Do NOT trigger for read-only tasks (e.g. answering questions, reviewing code without
  changes, generating one-off scripts that aren't saved to the repo). When in doubt, trigger it.
---

# Last Changes for session start only

!`git rev-parse --git-dir > /dev/null 2>&1 && git diff HEAD || echo "NOT_A_GIT_REPO"`

# Codebase Context Updater

After completing any meaningful code change, automatically discover and update all codebase
context documents so they reflect the current state of the project.

## Cross-repo detection

Before doing anything else, check whether the current working directory is itself a git repo:

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NOT_A_GIT_REPO"
```

**If the output is `NOT_A_GIT_REPO`** — this is a cross-repo project (a parent folder
containing multiple sibling repos). Find all immediate child directories that are git repos:

```bash
for dir in */; do
  if [ -d "$dir/.git" ]; then echo "$dir"; fi
done
```

For each one found, run Steps 1–5 **scoped to that subdirectory** (treat it as the project
root). Do not try to run `git diff` at the parent level — it has no repo.

**If the output is `true`** — this is a normal single repo. Continue with Step 1 below as
usual.

## Step 1: Discover context documents

Scan the project root and common locations for context files. These are files whose purpose
is to describe the codebase to humans or AI agents. Look for:

**Common filenames (case-insensitive):**
- `CLAUDE.md`, `CLAUDE.local.md`
- `README.md`, `README.rst`, `README.txt`
- `ARCHITECTURE.md`, `ARCHITECTURE.rst`
- `CONTEXT.md`, `CONTEXT.local.md`
- `CODEBASE.md`
- `AGENTS.md`
- `CONTRIBUTING.md`
- `DEVELOPMENT.md`, `DEVELOPMENT.local.md`
- `docs/architecture.md`, `docs/overview.md`, `docs/context.md`
- `.cursorrules`, `.aider.conf.md`, `copilot-instructions.md`
- **Any `.md` file inside a `.claude/` folder** (e.g. `.claude/CLAUDE.md`,
  `.claude/context.md`, `.claude/*.md`) - this is Claude Code's own config/context location
- Any `.md` file in a `docs/` or `.docs/` folder whose name suggests architectural or
  onboarding content

Run a quick scan:
```bash
# Named context files anywhere in the tree (up to 3 levels deep)
find . -maxdepth 3 \( -name "CLAUDE.md" -o -name "CLAUDE.local.md" -o -name "CONTEXT.md" \
  -o -name "ARCHITECTURE.md" -o -name "AGENTS.md" -o -name "README.md" \
  -o -name "DEVELOPMENT.md" -o -name "CONTRIBUTING.md" -o -name "CODEBASE.md" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/vendor/*" 2>/dev/null

# Every .md file inside any .claude folder
find . -type d -name ".claude" -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -exec find {} -name "*.md" \; 2>/dev/null
```

Read every file found. If none exist, go to **Step 4: Bootstrap**.

## Step 2: Understand what changed

Before writing, recall what was done in this session. Summarize mentally:

- Which files were created, modified, or deleted?
- Were new modules, services, routes, entities, or components introduced?
- Did dependencies change (`package.json`, `pyproject.toml`, `pom.xml`, `go.mod`, etc.)?
- Were environment variables, config files, or Docker/CI config changed?
- Were database migrations added?
- Was anything removed or renamed?

## Step 3: Update each context document

For each discovered file, apply targeted updates. Follow these rules:

**What to update:**
- Module/service/component listings: add new ones, remove deleted ones, rename renamed ones
- File structure sections: reflect new dirs/files if significant
- Architecture descriptions: update if the overall shape changed (new service, new layer, etc.)
- Dependency sections: update if `package.json`, etc. changed
- Environment variable sections: add new vars introduced
- "How to run" or setup sections: update if new steps are required
- API/route summaries: add new endpoints, remove deleted ones

**What NOT to change:**
- The existing style, tone, and formatting of the document
- Sections unrelated to what changed
- Project history, decisions, or rationale sections (unless you changed something they refer to)

**How to edit:**
- Use `str_replace` for targeted edits; never rewrite the whole file unless it is very short
- Keep edits minimal and precise
- If a section doesn't exist yet but is now needed (e.g. a new "Services" section), append it
  in a style consistent with the rest of the document

## Step 4: Bootstrap (no context documents found)

If no context documents exist, create a `CLAUDE.md` at the project root.

Explore the project structure first:
```bash
find . -maxdepth 3 -not -path "*/node_modules/*" -not -path "*/.git/*" \
  -not -path "*/vendor/*" -not -path "*/__pycache__/*" | sort
```

Then read key files: `package.json` / `pyproject.toml` / `pom.xml` / `go.mod`,
main entry points, and any existing config files.

Write a `CLAUDE.md` that covers:
1. **Project purpose** - what it does in 1-2 sentences
2. **Tech stack** - languages, frameworks, main libraries
3. **Project structure** - key directories and what they contain
4. **How to run** - dev server, build, test commands
5. **Key concepts** - domain terms, architectural patterns used
6. **Environment** - required env vars and what they do
7. **Important notes** - anything non-obvious that future Claude sessions should know

Keep it concise. Aim for under 150 lines. This file will grow over time.

## Step 5: Report

After all updates, briefly tell the user what was updated:

> "Updated `CLAUDE.md`: added `PaymentService` to the services section and documented the
> new `STRIPE_WEBHOOK_SECRET` env var."

One line per file updated. If nothing needed changing (the docs were already accurate),
say so:

> "Context docs are already up to date - no changes needed."

---

## Principles

- **Accuracy over completeness.** A short, accurate doc beats a long, stale one.
- **Minimal diffs.** Touch only what changed. Preserve the author's voice.
- **No hallucination.** Only document what actually exists in the codebase.
- **Silent by default.** Don't ask for permission - just do it and report at the end.
