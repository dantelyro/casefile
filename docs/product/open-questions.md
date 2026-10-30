# Open questions

- How does casefile behave on Windows without Git Bash, and should it? Claude Code then runs hook
  commands through PowerShell, where `sh ".../run-hook"` fails: every guard refuses with a raw error and
  `session_start` adds nothing. Options: one hook command valid in both shells with a `run-hook.ps1`
  launcher; a narrow skill whose description matches the failure and explains it; an output style with
  `force-for-plugin` (always on, no shell, but it replaces the user's style). Needs a live probe first:
  a throwaway plugin whose hook command does not exist, capturing what Claude receives on a refused edit
  and what a failing `SessionStart` shows. Blocks nothing yet. Answers: the probe, then the developer.
- M8, refactor existing code: how far may it reverse D-056? Pinning behaviour before a refactor needs
  tests for existing code, which D-056 dropped as a casefile path. Are those tests plain
  characterization tests inside the refactor, or spec rules? Blocks M8. Answers: the developer.
- M8: is refactor its own skill on a `refactor/` branch, driven like `fix-bug`, or a mode of
  `implement`? And how is a target bounded — a file, a folder, a module? Blocks M8. Answers: the
  developer.
