# Open questions

- Can the reviewer work in the implementer's worktree, one worktree per change instead of per agent
  run? Needs a live probe: whether an agent without `isolation` keeps its shell in another folder
  after `cd`, and whether the `cwd` the hooks see follows it. Blocks nothing yet. Answers: the probe.
- What is the docs reconciliation skill called: `docs-reconciliation`, or shorter (`migrate-docs`)?
  Blocks DOCS-008. Answers: the developer.
- Does it also cover devflow's own check of `docs/skill-authoring.md` against the CLI version, or only
  the layout? Blocks DOCS-001. Answers: the developer.
- How does devflow behave on Windows without Git Bash, and should it? Claude Code then runs hook
  commands through PowerShell, where `sh ".../run-hook"` fails: every guard refuses with a raw error and
  `session_start` adds nothing. Options: one hook command valid in both shells with a `run-hook.ps1`
  launcher; a narrow skill whose description matches the failure and explains it; an output style with
  `force-for-plugin` (always on, no shell, but it replaces the user's style). Needs a live probe first:
  a throwaway plugin whose hook command does not exist, capturing what Claude receives on a refused edit
  and what a failing `SessionStart` shows. Blocks nothing yet. Answers: the probe, then the developer.
