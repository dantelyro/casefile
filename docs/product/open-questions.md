# Open questions

- How does casefile behave on Windows without Git Bash, and should it? Claude Code then runs hook
  commands through PowerShell, where `sh ".../run-hook"` fails: every guard refuses with a raw error and
  `session_start` adds nothing. Options: one hook command valid in both shells with a `run-hook.ps1`
  launcher; a narrow skill whose description matches the failure and explains it; an output style with
  `force-for-plugin` (always on, no shell, but it replaces the user's style). Needs a live probe first:
  a throwaway plugin whose hook command does not exist, capturing what Claude receives on a refused edit
  and what a failing `SessionStart` shows. Blocks nothing yet. Answers: the probe, then the developer.
