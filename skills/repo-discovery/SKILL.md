---
name: repo-discovery
description: >
  Use when opening a codebase you have not worked in during this session — at session start,
  when the working directory changes, when asked to work in an unfamiliar repo or a sibling
  project, or before answering "where does X live" and "how do I run this". Triggers on: a
  parent folder holding several repos, a monorepo with workspaces, no obvious entry point, or
  needing to find a project's context documents before doing anything else.
---

# Repo Discovery

## Overview

Orienting in an unfamiliar codebase is a **read problem with a cost ceiling**. The failure is
not getting lost — it is burning half a context window on `find .` and vendored dependencies
before writing a line.

**Core principle: read the map before the territory.** A project's context documents were
written by someone who already understood it. Exhaust them first; explore the tree only for
what they do not answer.

## Order

1. **Shape** — is this even a repo, and what kind
2. **Map** — context documents
3. **Stack** — manifests, not source
4. **Entry points** — only now, and only what you need
5. **Report** — what you found and what you could not

Stop as soon as you can answer the question in front of you. Discovery is proportional to what
you are about to do: full discovery is for starting work in a repo, not for a one-line fix.

## Step 1: Shape

```bash
git rev-parse --is-inside-work-tree 2>/dev/null || echo "NOT_A_GIT_REPO"
```

**`NOT_A_GIT_REPO`** — likely a parent folder holding sibling repos. Git commands here fail or,
worse, resolve against an unrelated parent repo.

```bash
for dir in */; do [ -d "$dir/.git" ] && echo "$dir"; done
```

Treat each result as its own project root, and **ask which one** before scanning: a parent may
hold a dozen repos and the answer is usually one of them.

**`true`** — a single repo. Check whether it is a monorepo, because it changes where everything
lives:

```bash
git rev-parse --show-toplevel
cat package.json 2>/dev/null | grep -A5 '"workspaces"'
ls pnpm-workspace.yaml lerna.json nx.json turbo.json go.work Cargo.toml 2>/dev/null
```

In a monorepo, each workspace may have its own scripts, lint config and test command. The root
scripts often delegate — and often lie about what a sub-package actually does.

## Step 2: The map — context documents

These are written to explain the codebase. Read every one you find before opening source.

```bash
find . -maxdepth 3 \( -name "CLAUDE.md" -o -name "CLAUDE.local.md" -o -name "AGENTS.md" \
  -o -name "CONTEXT.md" -o -name "ARCHITECTURE.md" -o -name "CODEBASE.md" \
  -o -name "README.md" -o -name "DEVELOPMENT.md" -o -name "CONTRIBUTING.md" \) \
  -not -path "*/node_modules/*" -not -path "*/.git/*" -not -path "*/vendor/*" 2>/dev/null

# Agent config lives in dot-folders and is easy to miss
find . -type d \( -name ".claude" -o -name ".cursor" \) -not -path "*/node_modules/*" \
  -exec find {} -name "*.md" \; 2>/dev/null
ls .cursorrules .aider.conf.md .github/copilot-instructions.md 2>/dev/null

# A docs/ folder usually has the real architecture material
ls docs/ .docs/ 2>/dev/null
```

**Read them in this order:** agent instructions (`CLAUDE.md`/`AGENTS.md`) → architecture →
README → contributing. The first is written for exactly your situation and is the densest.
READMEs drift worst, because they are written once for a launch.

**Believe them provisionally.** A context document describes the repo as of its last update, so
a claim that contradicts the code is a finding, not truth.

**Found none?** Say so and offer to create one. See `evidence-based-decisions` for what to
propose and why the offer has to be answered first.

## Step 3: Stack, from manifests only

```bash
ls package.json pyproject.toml requirements.txt go.mod Cargo.toml pom.xml build.gradle \
   Gemfile composer.json *.csproj 2>/dev/null
cat package.json 2>/dev/null | head -40      # name, scripts, deps, engines
ls Dockerfile docker-compose.y*ml Makefile Taskfile.y*ml .nvmrc .tool-versions 2>/dev/null
ls .github/workflows/ 2>/dev/null            # CI is the honest "how to build"
```

The manifest tells you the stack in twenty lines. Inferring it from source costs hundreds and
gets it wrong.

**CI config is the most reliable "how to run"** — it is the version that actually has to work,
kept current by breaking when it is not. A README's setup section is under no such pressure, so
verify anything you take from it.

## Step 4: Entry points — narrowly

Only once you know the shape and stack, and only what the current task needs:

```bash
git ls-files | head -50                       # tracked only: no build output, no vendor
git ls-files | sed 's|/[^/]*$||' | sort | uniq -c | sort -rn | head -20   # where the code is
```

`git ls-files` beats `find` — it respects `.gitignore`, so `node_modules`, `dist` and
`coverage` never appear. The directory histogram shows where the mass of the project sits,
which is usually more informative than any single file.

**Never read `node_modules`, `vendor`, `dist`, `.venv`, or lockfiles.** They are enormous,
generated, and answer nothing the manifest does not.

## Step 5: Recent activity, if you are picking up work

```bash
git log --oneline -15
git log --oneline -10 --name-only | head -40   # what has been moving
git status --short
```

Recent commits tell you what the project is *currently* about, which the docs may not yet
reflect. If the project records a doc-reconciliation watermark, replay from it instead — see
`evidence-based-decisions`.

## Step 6: Report

State the shape, the map, how to run it, and — most usefully — **what you could not determine**:

> Monorepo, npm workspaces: `api/` (NestJS + Fastify, TS ESM) and `web/` (React + Vite).
> `CLAUDE.md` at root and `docs/architecture/` with a mental-model and decision log.
> Run: `npm install` at root; `npm test` needs Postgres via `docker-compose.yml`.
> Could not determine: whether `web/` is deployed separately — no CI workflow references it.

The gap list is the valuable half. It tells the reader which of your later statements are
grounded and which are inference.
