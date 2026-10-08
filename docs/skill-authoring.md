# Skill authoring — what Anthropic documents

**Verified against:** Claude Code `2.1.295` — 2026-10-08

Facts about how skills load and behave, taken from Anthropic's own pages. This file records what
the vendor says; the rules devflow layers on top live in `CLAUDE.md`. Each fact cites its page so a
version bump can be checked against the source rather than against this summary.

- **[CC]** Claude Code — Extend Claude with skills: https://code.claude.com/docs/en/skills
- **[BP]** Platform — Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- **[CL]** Claude Code changelog: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md

## Contents
- Loading and the trigger surface
- Frontmatter
- Progressive disclosure and references
- Body content and its lifetime
- Plugin skills
- Dynamic context and forks
- Testing
- Where the sources disagree

## Loading and the trigger surface

- Only `name` and `description` of every skill are in context at startup; `SKILL.md` loads when
  the skill is invoked, other files only when read. [BP][CC]
- `description` + `when_to_use` are truncated at **1,536 characters** in the skill listing
  (configurable with `skillListingMaxDescChars`). Put the key use case first. [CC]
- The whole listing has a budget of 1% of the model's context window. On overflow, Claude Code
  drops *descriptions* — least-invoked skills first — keeping only the names. [CC]
- Write descriptions in the **third person**: they are injected into the system prompt, and a
  mixed point of view causes discovery problems. State what the skill does *and* when to use it,
  with the key terms a user would say. [BP]
- A skill that triggers too often needs a more specific description, or
  `disable-model-invocation: true`. [CC]

## Frontmatter

- Read **only if the opening `---` is the file's first line**; otherwise the whole file is body. [CC]
- **YAML that fails to parse loads the skill with no fields set** — `/name` still works, automatic
  triggering silently does not. `claude plugin validate <dir>` finds the broken files (v2.1.233+);
  `--debug` shows the parse error. [CC]
- An unrecognised field name is ignored without an error, so a typo in a field name is silent. [CC]
- `name`: at most 64 characters, lowercase letters, digits and hyphens, no XML tags, must not
  contain `anthropic` or `claude`. `description`: non-empty, no XML tags. [BP]
- `disable-model-invocation: true` removes the description from context entirely — Claude cannot
  invoke it, and it is not preloaded into subagents. `user-invocable: false` hides it from the `/`
  menu but Claude can still invoke it. [CC]
- Outside Claude Code (claude.ai upload, Skills API) only `name`, `description`, `license`,
  `compatibility`, `metadata`, `allowed-tools` are allowed; any other key is a hard error. [CC]

## Progressive disclosure and references

- Keep the `SKILL.md` body **under 500 lines**; split into separate files as it approaches that. [BP][CC]
- **Keep references one level deep from `SKILL.md`.** For a file reached from another referenced
  file, Claude "might use commands like `head -100` to preview content rather than reading entire
  files, resulting in incomplete information." Files linked directly from `SKILL.md` are the ones
  expected to be read in full. [BP]
- A reference file **longer than 100 lines gets a table of contents at the top**, so a partial read
  still shows the file's full scope. [BP]
- `SKILL.md` should say what each supporting file contains and when to load it. [CC]
- Name files by content (`form_validation_rules.md`, not `doc2.md`) and use forward slashes in
  paths, even on Windows. [BP]
- Say whether a bundled script is to be **executed** or **read as reference**; executing costs only
  its output. [BP]

## Body content and its lifetime

- An invoked skill enters the conversation as one message and **stays across turns**; the file is
  not re-read. Write guidance as standing instructions, not one-time steps. [CC]
- After auto-compaction, the most recent invocation of each skill is re-attached, **first 5,000
  tokens only**, sharing a **25,000-token** budget filled from the most recently invoked skill.
  Older skills can be dropped entirely. **Put the most important instructions near the top.** [CC]
- A rule that must hold every time belongs in a hook — a skill can register one in its `hooks`
  frontmatter — not in prose Claude may stop following. [CC]
- Be concise: "Claude is already very smart" — add only context it does not have, and ask of each
  paragraph whether it justifies its token cost. Every line is a recurring cost once loaded.
  "State what to do rather than narrating how or why." Testing on Opus should check the skill
  "avoids over-explaining". [BP][CC] Use one term per concept throughout. Avoid time-sensitive statements; keep superseded
  methods under an "old patterns" heading. [BP][CC]
- Match specificity to fragility: exact commands for fragile, ordered operations; heuristics where
  many approaches are valid. Give one default with an escape hatch, not a menu of options. [BP]
- `allowed-tools` grants clear on the next user message even though the content stays. [CC]

## Plugin skills

- Plugin skills load from `<plugin>/skills/<name>/SKILL.md` and are namespaced
  `/plugin-name:skill-name`, so they never clash with other locations. [CC]
- **`skillOverrides` does not apply to plugin skills** — they are managed through `/plugin`. [CC]
- `${CLAUDE_PLUGIN_ROOT}` and `${CLAUDE_PLUGIN_DATA}` are substituted only in plugin skills;
  `${CLAUDE_SKILL_DIR}` is the skill's own subdirectory, not the plugin root. [CC]
- Plugin skills do not load in cloud sessions when the plugin is enabled only in user settings or
  declared in the repo's `.claude/settings.json`. [CC]
- Subagents preload at most 32 skills from their `skills` field (v2.1.295). [CL]

## Dynamic context and forks

- `` !`command` `` and ```` ```! ```` blocks run before Claude sees the skill; **any failure aborts the
  whole invocation**. With bash, non-zero exits fail except exit 1 from search/compare commands;
  append `|| true` where non-zero is expected. Each command has a 2-minute timeout. [CC]
- Injected commands never prompt: anything not allowed by permission rules (outside auto mode)
  aborts the invocation. They do not run for skills synced from claude.ai, and
  `disableSkillShellExecution` replaces them with a placeholder. [CC]
- `context: fork` starts a subagent with the skill as its only prompt — no conversation history.
  It only works for skills that contain a task. `agent: Explore`/`Plan` also skip `CLAUDE.md`. A
  backgrounded fork's edits are outside `/rewind`. [CC]

## Testing

- Seeing a skill trigger proves it was found, not that it worked. Compare each realistic prompt in a
  fresh session with and without the skill. [CC]
- For a plugin, `claude plugin eval` runs each prompt with and without the plugin and can gate CI;
  a `tool_used: Skill` grader measures triggering across prompts. [CC]
- Build at least three evaluations before writing extensive content, and test on every model the
  skill will run on — what suffices for Opus may be too thin for Haiku. [BP]

## Where the sources disagree

- **Description length:** [BP] caps `description` at **1,024** characters; [CC] truncates
  `description` + `when_to_use` at **1,536**. Staying under 1,024 satisfies both.
