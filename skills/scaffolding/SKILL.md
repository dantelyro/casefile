---
name: scaffolding
description: >
  Use when creating a new project from nothing — a monolith, an API, a microservice, or a
  separated backend and frontend — and when `/init` is run in a directory that holds no project
  yet. Triggers on: "create a new project", "scaffold a backend", "start a new API", "set up a
  new repo", an empty directory about to become a project, or adding a frontend or backend
  beside an existing one. Not for adding features, modules or entities to a project that already
  exists.
---

# Scaffolding

## Overview

A scaffold's failure mode is not a missing file — it is a project **born stale**. Dependency
versions typed from memory, a config lifted from a two-year-old repo, a generator's output
quietly overwritten by hand. The project is three months behind on the day it is created, and
nobody can tell which parts were chosen and which were remembered.

**Core principle: the generator owns versions, you own content.** Never type a version number.
Run the generator, add packages by name, let npm resolve what current means. Config files you
write; manifests you never hand-edit.

That line is the whole skill. Everything below is what it takes to hold it.

## Precedence over `/init`

`/init` documents what exists. In a directory with no project in it, there is nothing to
document, so **scaffolding runs first** and `/init` runs in phase 4, once there is a repo to
describe. If the directory already holds a project, this skill does not apply and `/init`
proceeds normally.

## Four phases

**1. Interrogate.** Every question asked up front, nothing written to disk. The set, its order
and what each answer changes: `references/questions.md`. What is never asked, because it is
already decided: `references/invariants.md`.

**2. Plan.** Write `scaffold.plan.md` — the answers, then every command in execution order with
its exact flags, then every file the skill will write and why no generator emits it. **Stop.**
The user reads it, edits it, approves it. Format: `references/plan-format.md`.

**3. Execute.** Run the plan top to bottom. **Generators first, written config second** — a
generator run after hand-written files overwrites them without asking. Add every dependency by
name.

**4. Verify.** Run the build, the test suite, and `predev` for real — boot the containers, apply
the migrations. Then `/init`, then propose the doc set through `evidence-based-decisions`.

## Built is not verified

A scaffold that has never been executed is a guess with good formatting. Run it, and report the
two axes separately — *"generated, not yet run"* is honest, *"done"* is not. This is the same
distinction `evidence-based-decisions` draws, and it applies hardest here: the failure surfaces
on someone else's machine, on their first `npm run dev`.

## Generator flags are Grade 3 until they run

A command written from memory is prose documentation of a CLI — a hypothesis, not a fact.
Generators rename flags, add prompts, and change defaults between minor versions.
`references/generators.md` records each command **with its verification state**. When a command
fails or stops on a prompt, fix that file in the same change. A flag set that has been run is
worth more than one that reads correctly.

**Interactivity is the specific hazard.** A generator that stops for a prompt hangs the session —
there is no TUI to answer. Every command in the plan must be non-interactive, or the reference
must record the exact answer sequence.

## Never ask what is already decided

The invariants exist so that two projects scaffolded a year apart are the same project. Every
question is a chance to produce something unlike the last one, so the question set is closed:
adding to it is a decision, not a convenience.

## Red flags — stop

- A version number in a command or a manifest that you typed
- Editing `package.json` by hand instead of running `npm i`
- Writing a config file before the generator that owns that directory has run
- Reporting the scaffold done when no command in it has been executed
- A generator command in the plan that you have never run and have not marked unverified
- Asking a question `references/invariants.md` already answers
- Continuing past phase 2 without the plan being approved

## Rationalizations

| Excuse | Reality |
|---|---|
| "I know the current version of that package" | You know the version as of your training data. `npm i <pkg>` costs nothing and is never wrong. |
| "The generator's defaults are close enough, I'll fix the config after" | Fixing after is fine. Writing files the generator will overwrite is not — order is load-bearing. |
| "It'll obviously work, no need to run it" | Then running it costs one minute. Scaffolds fail on paths, ports and peer deps, none of which read wrong. |
| "One more question won't hurt" | Every optional question is a way for two projects to diverge. That divergence is what this skill exists to prevent. |
| "I'll write the plan as I go" | The plan exists to be rejected before anything is on disk. Written afterwards it is a changelog. |
| "The user is in a hurry, I'll skip the approval stop" | A wrong scaffold costs more than the stop. Deleting a generated project is not free. |

## References

- `references/questions.md` — the question set, order, follow-ups, what each answer changes
- `references/invariants.md` — what is always applied and never asked
- `references/generators.md` — exact non-interactive commands, and their verification state
- `references/backend.md` — Nest / Express / Fastify layout, and the cross-cutting backend set
- `references/frontend-react.md` — the greenfield stack and its three component branches
- `references/frontend-vue.md` — the Quasar legacy stack, deliberately frozen
- `references/release.md` — semantic-release and GitLab CI
- `references/plan-format.md` — what `scaffold.plan.md` must contain
