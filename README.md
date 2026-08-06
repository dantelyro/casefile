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

Development workflow skills.

| Skill | What it does |
| --- | --- |
| `context-updater` | Discovers a project's context documents (`CLAUDE.md`, `README.md`, `ARCHITECTURE.md`, anything under `.claude/`) and updates them to match the code after a change. Handles both single repos and cross-repo parent folders. |

## Layout

```
.claude-plugin/
  marketplace.json      # makes this repo a marketplace
plugins/
  devflow/
    .claude-plugin/
      plugin.json       # makes this folder a plugin
    skills/
      context-updater/
        SKILL.md
```

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
