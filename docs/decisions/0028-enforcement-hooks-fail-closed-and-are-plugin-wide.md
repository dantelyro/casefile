# D-028 — Enforcement hooks fail closed and are plugin-wide

**Status:** Accepted (2026-10-15). Supersedes D-005.
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session. Scope, 2026-10-14:
"i enforce the rules in the entire devflow if it annoys me i will remove later". Requiring Git for
Windows and replacing the polyglot with a plain `sh` starter, 2026-10-15: "yes, commit them" and
"yes simplify it and commit".
**Implemented by:** `f40cfcb` — 2026-10-15 (registration), `d2dbf0d` (the `sh` starter).

**Context:** D-005 made the hook wrapper exit 0 silently when no bash was found: right for optional
context, wrong for a guard. The 0.13.0 probe (`tests/fixtures/`, results in the 0.13.0 spec) measured
three facts on Claude Code 2.1.300: a hook that crashes or times out **lets the action through**
unless it is registered with `onFailure: "block"`; plugin hooks fire in the main session, in plugin
agents and in built-in agents; and a hook command written for bash does not parse under PowerShell,
whose own form (`& "<path>" <args>`) is a syntax error in bash. Claude Code runs hook commands under
Git Bash on Windows and falls back to PowerShell only when Git Bash is missing.

**Options:** (a) keep D-005's polyglot and silent exit, accepting unguarded actions when a hook
breaks; (b) fail closed per guard (`run.py` denies on any error, `onFailure: "block"` plus a
timeout on every guard), apply the guards in every project where devflow is enabled, run every hook
through one `sh` starter, and require Git for Windows; (c) as (b), but register each guard twice,
once in a PowerShell-compatible form.

**Decision:** (b). Every guard denies when its hook is unknown, its input unreadable, its config or
design system unusable, or it crashes; Claude Code refuses the call when a guard crashes or hangs.
The guards apply to every session with devflow enabled — the developer's included for the
*everyone* rows. `hooks/run-hook` is plain `sh`; D-005's cmd/bash polyglot, written for a cmd.exe
devflow no longer runs under, is retired with the bash hook it served. Windows requires Git for
Windows, stated in the README. Session start alone never blocks: it only adds context.

**Trade-offs:** A devflow bug now refuses commands instead of letting them pass — loud by design,
and the reason says it is a devflow bug. On Windows without Git Bash nothing of devflow's can run,
so devflow cannot even explain that itself: the developer sees Claude Code's hook error and the
guarded calls are refused. The rules hold in every project with devflow enabled, including ones
that did not ask for them; the developer accepted that and may remove a rule that annoys.
(c) was rejected: two registrations per guard would run twice under Git Bash, and keeping them in
step is the hand-maintained duplication D-005 itself avoided.
