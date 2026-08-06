# dantelyro plugins

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace.

## Install

```
/plugin marketplace add dantelyro/devflow
/plugin install devflow@dantelyro
```

Claude Code refreshes known marketplaces on startup, so once installed, later
changes pushed here are picked up automatically.

## Plugins

### `devflow`

Workflow skills for keeping a codebase understandable — orienting in it, and recording
why it is the way it is.

| Skill | What it does |
| --- | --- |
| `repo-discovery` | Orients you in an unfamiliar codebase: detects repo shape (single, monorepo, or a parent folder of siblings), finds the context documents (`CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md`, anything under `.claude/`), reads the stack from manifests rather than source, and reports what it could **not** determine. Built around a cost ceiling — read the map before the territory. |
| `evidence-based-decisions` | Keeps the reasoning record true. Decision-log format and superseding, grading evidence when integrating with a system you do not control, and the discipline that separates *built* from *verified*. Includes a commit watermark, so you can tell what changed while you were away. |

The two compose: `repo-discovery` answers what a project **is**, `evidence-based-decisions`
answers **why** — and keeps that answer honest as the code moves.

Neither creates architecture documents in a project that has not asked for them. They propose
and wait.

## Layout

```
.claude-plugin/
  marketplace.json      # makes this repo a marketplace
plugins/
  devflow/
    .claude-plugin/
      plugin.json       # makes this folder a plugin
    skills/
      repo-discovery/
        SKILL.md
      evidence-based-decisions/
        SKILL.md
        references/     # loaded on demand, not with the skill
          decision-log.md
          living-documents.md
          verifying-external-systems.md
```

A skill's `SKILL.md` is what gets loaded when it triggers, so it stays small. Anything long —
formats, procedures, reference material — goes in `references/` and is read only when the work
actually needs it.

The two `.claude-plugin` folders do different jobs: the outer one declares the
marketplace and lists what it offers, the inner one declares a single plugin.

## Adding a plugin

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
