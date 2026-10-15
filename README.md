# dantelyro plugins

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace.

## Install

**Requires** Python 3.10 or newer, and on Windows [Git for Windows](https://gitforwindows.org)
(Claude Code runs devflow's hooks through its Git Bash). If Python is missing, devflow says so at
the start of a session and asks before installing it; its guards refuse commands until then.

```
/plugin marketplace add dantelyro/devflow
/plugin install devflow@dantelyro
```

Then turn auto-update on: `/plugin` → **Marketplaces** → `dantelyro` → **Enable
auto-update**. Third-party and local marketplaces have it **off** by default — only
Anthropic's own marketplaces ship with it enabled — so without this step an install
stays on the version it was fetched at, forever.

With it on, Claude Code refreshes the marketplace shortly after a session starts, on
a random delay of up to ten minutes, and the new version loads on the next launch or
when you run `/reload-plugins`. Never mid-session.

An update only happens when `version` in `plugin.json` changes. Push new commits
without bumping it and every existing install keeps the cached copy.

## Plugins

### `devflow`

Workflow skills for keeping a codebase understandable — orienting in it, and recording why it is
the way it is.

| Skill | What it does |
| --- | --- |
| `repo-discovery` | Orients you in an unfamiliar codebase: detects repo shape (single, monorepo, or a parent folder of siblings), finds the context documents (`CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md`, anything under `.claude/`), reads the stack from manifests rather than source, and reports what it could **not** determine. Built around a cost ceiling — read the map before the territory. |
| `evidence-based-decisions` | Keeps the reasoning record true. Decision-log format and superseding, grading evidence when integrating with a system you do not control, and the discipline that separates *built* from *verified*. Includes a commit watermark, so you can tell what changed while you were away. |

The two compose: `repo-discovery` answers what an existing project **is**, and
`evidence-based-decisions` answers **why** — and keeps that answer honest as the code moves.

Neither of them creates architecture documents in a project that has not asked for them. They
propose and wait.

#### Why there is a hook

A skill fires when the model recognises its `description` in the situation in front of it. That
works for `repo-discovery`, whose triggers are things a person actually types — *where does X
live*, *how do I run this*, *an unfamiliar repo*.

It does not work for `evidence-based-decisions`. Its primary trigger is **the start of a
session**, and no first message ever says so. Its other triggers are facts about the repo — the
project keeps a decision log; the docs are behind `HEAD` — which cannot be recognised before
reading the repo, and reading the repo is what the skill is for.

So the session-start hook (`hooks/devflow_hooks/session_start.py`) injects the trigger the prompt cannot supply: a short directive naming
the skill, emitted on `startup`, `clear` and `compact`. It injects a **pointer, not the skill
body** — the `Skill` tool loads the content on demand, keeping the per-session cost to a few
hundred tokens rather than the whole file.

## Layout

```
.claude-plugin/
  marketplace.json      # makes this repo a marketplace
  plugin.json           # makes it a plugin too — source is "./"
hooks/
  hooks.json            # auto-discovered; no plugin.json entry needed
  run-hook              # sh starter: finds Python 3.10+, runs run.py
  run.py                # runs one hook; refuses the call if the hook fails
  devflow_hooks/        # the hooks, standard-library Python
tests/                  # python -m unittest discover -s tests
skills/
  repo-discovery/
    SKILL.md
  evidence-based-decisions/
    SKILL.md
    references/         # loaded on demand, not with the skill
      decision-log.md
      living-documents.md
      verifying-external-systems.md
docs/
  decisions/            # why this repo is the way it is; one file per decision
    README.md           # generated index: id, title, status
```

This repo is both the marketplace and the single plugin it offers — the marketplace entry points
at `./`, so the two manifests sit side by side in one `.claude-plugin/` folder rather than nested.

A skill's `SKILL.md` is what gets loaded when it triggers, so it stays small. Anything long —
formats, procedures, reference material — goes in `references/` and is read only when the work
actually needs it.

The two manifests do different jobs: `marketplace.json` declares the marketplace and lists what
it offers, `plugin.json` declares the `devflow` plugin itself.

## Adding a plugin

A second plugin needs its own folder, since `devflow` occupies the root:

1. Create `plugins/<name>/.claude-plugin/plugin.json` with `name`, `description`
   and `version`.
2. Add its content — `skills/`, `commands/`, `agents/`, `hooks/`, `.mcp.json`.
3. Append an entry to the `plugins` array in `.claude-plugin/marketplace.json`
   pointing at `./plugins/<name>`.

Plugins are enabled independently per project, so splitting unrelated skills
into separate plugins is usually worth the extra manifest.

## Local development

Register the working copy as a marketplace to test changes before pushing:

```
/plugin marketplace add D:\projects\personal\devflow
```

## License

MIT
