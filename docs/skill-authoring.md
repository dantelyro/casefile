# Skill authoring — what Anthropic documents

**Verified against:** Claude Code `2.1.307` — 2026-10-21

Facts about how skills load and behave, taken from Anthropic's own pages. This file records what
the vendor says; the rules devflow layers on top live in `CLAUDE.md`. Each fact cites its page so a
version bump can be checked against the source rather than against this summary.

- **[CC]** Claude Code — Extend Claude with skills: https://code.claude.com/docs/en/skills
- **[BP]** Platform — Skill authoring best practices: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
- **[CL]** Claude Code changelog: https://raw.githubusercontent.com/anthropics/claude-code/main/CHANGELOG.md
- **[HK]** Claude Code — Hooks reference: https://code.claude.com/docs/en/hooks
- **[PL]** Claude Code — Plugin components and manifest reference: https://code.claude.com/docs/en/plugins/components, https://code.claude.com/docs/en/plugins-reference
- **[CLI]** Claude Code — CLI reference: https://code.claude.com/docs/en/cli-reference
- **[OS]** Claude Code — Output styles: https://code.claude.com/docs/en/output-styles

## Contents
- Loading and the trigger surface
- Frontmatter
- Progressive disclosure and references
- Body content and its lifetime
- Plugin skills
- Plugin hooks and agents
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
- The listing budget can be raised (`skillListingBudgetFraction`, `SLASH_COMMAND_TOOL_CHAR_BUDGET`),
  and low-priority skills set to `"name-only"` in `skillOverrides` to free it. `/skill-doctor`
  (v2.1.252+) finds unused skills. [CC]
- Skills could drop out of the model's listing after `/rewind`, fixed in v2.1.301. [CL]
- After compaction the skill list is sent to Claude again; `/reload-skills` sends only new or changed
  skills, and resumed and cloud sessions no longer resend the whole list on every plugin reload
  (v2.1.304). [CL]
- A skill whose file or folder name holds hidden, direction-changing or blank-like characters, `<` or
  `>`, is not offered until renamed (v2.1.299). [CL]

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
- A skill's own `hooks` are capped at 1,024 per source (a repo, your folder, or a plugin), a `once`
  hook no longer removes another skill's identical hook, and under a policy that allows hooks from
  plugins only, skills' hooks follow it (v2.1.304). [CL]
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
- Plugins that Claude Desktop mounts by path lose their `allowed-tools` when managed settings set `allowManagedPermissionRulesOnly` (v2.1.305). [CL]
- Subagents preload at most 32 skills from their `skills` field (v2.1.295). [CL]
- Startup with many plugins takes far fewer file-system calls for command and agent files (v2.1.302);
  the PowerShell tool finds commands in a plugin's `bin/` folder (v2.1.302). [CL]
- A plugin could keep a headless run going past `--max-turns`; fixed in v2.1.304. [CL]
- **A `CLAUDE.md` at the plugin root is not loaded:** "Claude Code doesn't load a `CLAUDE.md` at the
  plugin root, and `claude plugin validate` warns `CLAUDE.md at the plugin root is not loaded as
  project context`. To include instructions in a plugin, write them as a skill." devflow's root
  `CLAUDE.md` therefore reaches only sessions in this repository, and validate warns about it. [PL]
- A plugin's always-on text without a hook: an output style in `output-styles/` with
  `force-for-plugin: true` is applied whenever the plugin is enabled, overriding the user's
  `outputStyle`; the first loaded plugin that sets it wins, and without `keep-coding-instructions:
  true` it drops the default coding instructions. A style "gives Claude instructions to follow. It
  doesn't guarantee that something always happens." [OS] A plugin's `settings.json` honours only
  `agent` and `subagentStatusLine`, so it cannot add text. [PL]

## Plugin hooks and agents

Facts behind devflow's hooks and agents (0.13.0 spec). Quotes were taken through a summarising fetch
on 2026-10-15; the 0.13.0 probe checks the ones the hooks depend on against a live session.

- `hooks/hooks.json` at the plugin root is merged with whatever the manifest declares; plugin hooks
  merge with user and project hooks. [PL][HK] Two enabled plugins with the same name: one's hooks are
  left out, and `/plugin` notes it (v2.1.296). [CL]
- **Plugin hooks also run inside subagents**, and tool events there carry `agent_id` and `agent_type`.
  [HK]
- `agent_type` is present "when the session uses `--agent` or the hook fires inside a subagent". For
  a plugin's agent it is the plugin-scoped name, `my-plugin:reviewer`, not the bare frontmatter name.
  `agent_id`'s presence in the main session is not documented. [HK]
- PreToolUse `permissionDecision`: `allow`, `deny`, `ask`, `defer` (`defer` is ignored with a warning in
  interactive sessions). Whether `ask` works for a subagent's call is not documented. [HK] The
  permission prompt an `ask` raises names the plugin or skill whose hook asked (v2.1.301). [CL]
- **Exec form** when `args` is set: `command` resolved on `PATH`, no shell. On Windows it must be a real
  `.exe` — `.cmd`/`.bat` shims cannot be spawned. **Shell form** otherwise: `sh -c` on macOS/Linux, Git
  Bash on Windows, PowerShell when Git Bash is missing; `shell` (`bash`/`powershell`) is ignored in exec
  form. [HK]
- **A failing hook lets the action through by default:** an exit code other than 0 or 2 is a
  non-blocking error, and a timed-out hook does not block. `onFailure: "block"` (v2.1.295+) refuses
  the action instead. [HK] 2.1.299 fixed Windows PreToolUse hooks with no `shell` failing open when Git
  for Windows is missing, and made actions a plugin hook can block refused when the hook cannot be
  handed them or cannot answer. [CL]
- `if` takes exactly one permission rule, runs only on tool events, and is best-effort: when Claude
  Code cannot tell which commands a Bash input runs, the hook runs regardless. The page says to use
  the permission system, not a hook, for a hard allow or deny. [HK]
- A PreToolUse hook's deny reason was replaced by a timeout error; fixed in v2.1.304. Prompt and agent
  hooks run at most 12 of one event at a time (v2.1.302); devflow's hooks are command hooks. [CL]
- `updatedInput` from PreToolUse is validated like Claude's own input: unknown keys dropped, input the
  tool rejects denies the call (v2.1.300). [CL]
- `UserPromptSubmit` hooks run before a skill or slash command expands, so blocking the prompt also
  stops the skill's embedded commands (v2.1.299). [CL]
- **Plugin agents** live under `agents/`, loaded recursively; subfolders join the name
  (`agents/review/security.md` → `my-plugin:review:security`). Supported frontmatter: `name`,
  `description`, `model`, `effort`, `maxTurns`, `autoCompactWindow` (v2.1.296), `tools`,
  `disallowedTools`, `skills`, `memory`, `background`, `omitClaudeMd`, `isolation` (only
  `"worktree"`), `color`. **Ignored:** `permissionMode`, `hooks`, `mcpServers`, `initialPrompt` — an
  agent's rules have to be plugin hooks. Malformed frontmatter loads the agent with every field
  ignored. [PL] Which branch a plugin agent's worktree starts from is not documented. New worktrees in a bare repository sometimes started from local HEAD instead of the default branch, and unchanged subagent worktrees were sometimes not cleaned up; fixed in v2.1.305. [CL] Subagents that were messaged
  or resumed sometimes forgot their latest work; fixed in v2.1.304. Fork subagents (`subagent_type:
  "fork"`) are on by default in `claude -p` (v2.1.302). [CL]
- `claude --plugin-dir <path>` loads a plugin for one session without installing it; the plugin is
  named after the directory. [CLI][PL]

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
  a `tool_used: Skill` grader measures triggering across prompts. [CC] `--disallow-tools` and a
  `disallowed_tools` case field keep built-in tools (such as Agent) out of a run; a run that ends on
  an API error now scores 0 and fails the suite (v2.1.299). [CL]
- Build at least three evaluations before writing extensive content, and test on every model the
  skill will run on — what suffices for Opus may be too thin for Haiku. [BP]

## Where the sources disagree

- **Description length:** [BP] caps `description` at **1,024** characters; [CC] truncates
  `description` + `when_to_use` at **1,536**. Staying under 1,024 satisfies both.
- **Evaluations:** [BP] says there is no built-in way to run skill evaluations; [CC] documents
  `claude plugin eval`. [CC] is the newer and more specific source.
