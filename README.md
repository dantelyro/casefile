# dantelyro plugins

A personal [Claude Code](https://claude.com/claude-code) plugin marketplace.

## Install

**Requires** Python 3.10 or newer, and on Windows [Git for Windows](https://gitforwindows.org)
(Claude Code runs casefile's hooks through its Git Bash). If Python is missing, casefile says so at
the start of a session and asks before installing it; its guards refuse commands until then.

```
/plugin marketplace add dantelyro/casefile
/plugin install casefile@dantelyro
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

### `casefile`

Workflow skills and guards — orienting in a codebase, recording why it is the way it is, building
a milestone of spec rules in the main session, fixing bugs test-first, reviewing changes against
their specs with an isolated agent, and hooks that hold the rules every time.

| Skill | What it does |
| --- | --- |
| `repo-discovery` | Orients you in an unfamiliar codebase: detects repo shape (single, monorepo, or a parent folder of siblings), finds the context documents (`CLAUDE.md`, `AGENTS.md`, `ARCHITECTURE.md`, anything under `.claude/`), reads the stack from manifests rather than source, and reports what it could **not** determine. Built around a cost ceiling — read the map before the territory. |
| `review` | Gets a verdict on one change — a branch, a PR, a task from `docs/plans/`, a fix for an issue in `docs/issues/` — from the isolated `casefile:reviewer` agent, which checks it against its task and the project's spec rules, re-runs the tests itself, and answers approve or changes-requested with findings. Runs only when you ask; never merges or fixes. |
| `write-specs` | Turns a feature description, or the notes of a brainstorm that has ended, into spec rules with IDs (`### JOBS-020 · Title`), product decisions, decision entries, open questions and a new milestone in the build order. It drafts everything, asks the open questions together, and writes nothing until you say yes; `spec_lint.py` checks the specs hold together. Never starts or interrupts a brainstorm. |
| `implement` | Builds one milestone of spec rules (`### MATCH-010 · Title` headings) in the main session, with no agent: it checks the milestone against your decisions, then writes its plan in `docs/plans/` — small tasks tied to rule IDs, test-first for each rule about what the code does, each naming the existing code it can reuse — and after your approval builds each task on a `feat/` branch you name, one at a time in your checkout, test-first, and commits it once, with its status, after your yes. No merge commits, no status-only commits. You merge the branch into `main`; casefile never does. The plan is the progress record, so a later session resumes from it; `plan_status.py` picks the next task and `rules_coverage.py` reports each rule it checks as covered by a test, untested with its reason, or missing, and the finish report hands the `[MANUAL]` rules to you to test by hand. |
| `fix-bug` | Fixes one bug properly: the bug is a file in `docs/issues/`, reproduced with a failing test and fixed in the main session on a `fix/` branch you name ([`shared/work-branch.md`](shared/work-branch.md)), committed once after your yes, and you merge the branch. `issues_status.py` lists open issues and what they block, and checks every fixed one against the repository. |
| `evidence` | Keeps the reasoning record true. Decision-log format and superseding, grading evidence when integrating with a system you do not control, and the discipline that separates *built* from *verified*. Includes a commit watermark, so you can tell what changed while you were away. |

The two compose: `repo-discovery` answers what an existing project **is**, and
`evidence` answers **why** — and keeps that answer honest as the code moves.

None of them creates documents in a project that has not asked for them. They propose and wait —
including `review`, which proposes `.claude/casefile.json` on first use.

#### Guards

Hooks, on in every project where casefile is enabled, failing closed (D-028). The full table is in
`docs/specs/history/2026-10-14-review-design.md`, *Guard rules*.

- `git push` asks you, whether it comes from your session or from an agent (D-029).
- `docker compose down -v` and `--no-verify` are refused to everyone.
- `casefile:reviewer` edits only product code in your checkout, never tests, records, settings or the
  project's protected paths, may `git restore` and never switches branches. No other agent has rules
  of its own (GUARD-009).
- Every commit: no skipped or focused tests, the design check on added UI lines, and the test
  command of every configured app it touches.
- UI code may use only what the project's design system (`tokens.json`) defines.

#### `.claude/casefile.json`

Per-project settings the guards, the skills and the reviewer read; every key optional, and casefile never writes it
unasked. Each app names its own test command (whatever the project uses: `npm test`, `npx vitest
run`, `uv run pytest -q`…) and runs in its folder — `path`, defaulting to the app's name; `"."` is
the whole repository. `lint` is optional: when set, the commit gate and the reviewer run it next to
`test`. The skipped-test check knows Node and Python test files only. `install` installs the app's
locked dependencies; `image` rebuilds the app's container before a task that touched it is committed.
`specs_dir`, `plans_dir` and `build_order` (the page whose "Build order" section lists the
milestones) tell `implement` where things are; the values shown are the defaults.

Frontend and backend in separate repositories: give each `"repo"` (its own name) and `"siblings"`
(the others' names and relative paths, `{"backend": "../backend"}`), and list those paths in
`permissions.additionalDirectories`. Both repositories then hold the same specs, milestone and plan;
each task's `Repo:` says which one builds it, and each reads the other's plan for the status of the
tasks it does not build (D-041).

```json
{
  "default_branch": "main",
  "protected_paths": ["docs/specs/", "docs/plans/", "docs/issues/", "docs/product/"],
  "specs_dir": "docs/specs", "plans_dir": "docs/plans", "build_order": "docs/product/blueprint.html",
  "apps": { "web": { "test": "npm test", "lint": "npm run lint", "install": "npm ci",
                     "image": "docker compose build web" } },
  "design": { "tokens": "docs/product/design-system/tokens.json", "ui_paths": ["web/"],
              "components_dir": "web/components/ui/", "classes": "tailwind" }
}
```

#### Why there is a hook

A skill fires when the model recognises its `description` in the situation in front of it. That
works for `repo-discovery`, whose triggers are things a person actually types — *where does X
live*, *how do I run this*, *an unfamiliar repo*.

It does not work for `evidence`. Its primary trigger is **the start of a
session**, and no first message ever says so. Its other triggers are facts about the repo — the
project keeps a decision log; the docs are behind `HEAD` — which cannot be recognised before
reading the repo, and reading the repo is what the skill is for.

So the session-start hook (`hooks/casefile_hooks/session_start.py`) injects the trigger the prompt cannot supply: a short directive naming
the skill, emitted on `startup`, `clear` and `compact`. It injects a **pointer, not the skill
body** — the `Skill` tool loads the content on demand, keeping the per-session cost to a few
hundred tokens rather than the whole file. Ahead of it comes the project context: where your
decisions are, and that dropped work stays dropped. No agent is given either.

## Layout

```
.claude-plugin/
  marketplace.json      # makes this repo a marketplace
  plugin.json           # makes it a plugin too
hooks/
  hooks.json            # auto-discovered; no plugin.json entry needed
  run-hook              # sh starter: finds Python 3.10+, runs run.py
  run.py                # runs one hook; refuses the call if the hook fails
  casefile_hooks/        # the hooks, standard-library Python
tests/                  # uv run pytest
evals/                  # trigger evals, billed: claude plugin eval . --ablation none --scaffold
agents/
  reviewer.md           # casefile:reviewer, dispatched only by review
shared/
  work-branch.md        # naming and creating the feat/ or fix/ branch the developer merges
  build-task.md         # building one task or fix test-first, for implement and fix-bug
skills/
  fix-bug/
    SKILL.md
    scripts/issues_status.py
  implement/
    SKILL.md
    references/planning.md      # how the main session plans a milestone, and the plan format
    scripts/plan_status.py      # the next batch, stuck tasks, tasks waiting on an issue
    scripts/rules_coverage.py   # each rule it checks: tested, untested with a reason, or missing
  write-specs/
    SKILL.md
    references/specs-layout.md  # the layout, rule format, README and product files
    scripts/spec_lint.py        # headings, unique IDs, tags, build order, links, file table
  review/
    SKILL.md
  repo-discovery/
    SKILL.md
  evidence/
    SKILL.md
    references/         # loaded on demand, not with the skill
      decision-log.md
      living-documents.md
      new-project-docs.md
      verifying-external-systems.md
    scripts/            # decision_new.py, decision_index.py
docs/
  decisions/            # why this repo is the way it is; one file per decision
    README.md           # generated index: id, title, status
  specs/                # casefile's own spec rules; history/ holds designs of 0.12–0.16
  product/              # build order (blueprint.md), product decisions, open questions
  plans/                # milestone plans, the progress record of implement
  issues/               # bugs, one file each, for fix-bug
  skill-authoring.md    # what Anthropic documents about skills, version-watermarked
```

This repo is both the marketplace and the single plugin it offers — the plugin is the repository
root, so the two manifests sit side by side in one `.claude-plugin/` folder rather than nested; the
marketplace entry fetches it from GitHub over HTTPS.

A skill's `SKILL.md` is what gets loaded when it triggers, so it stays small. Anything long —
formats, procedures, reference material — goes in `references/` and is read only when the work
actually needs it.

The two manifests do different jobs: `marketplace.json` declares the marketplace and lists what
it offers, `plugin.json` declares the `casefile` plugin itself.

## Adding a plugin

A second plugin needs its own folder, since `casefile` occupies the root:

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
/plugin marketplace add C:\Users\beyon\projects\casefile
```

## License

MIT
