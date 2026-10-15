# `review` and the enforcement foundation — design

**Date:** 2026-10-14.
**Status:** Approved 2026-10-14. Not yet implemented.
**Release:** `0.13.0`. Comes after the removal of `mvp` and `project-specs` (0.12.0); `fix-bug`
(0.14.0), `implement` (0.15.0) and `write-specs` (0.16.0) build on it.
**Origin:** the agent workflow used to build Inverso milestones M0–M1 (`.claude/skills/build-milestone`,
`.claude/agents/*`, `.claude/hooks/*` in that repo), generalised.

## Summary

devflow gains its first agent and its first enforcement:

| Piece | What it is |
|---|---|
| `devflow:reviewer` agent | Reviews one change against its plan task or bug report and the project's specs, re-runs the tests, returns `approve` or `changes-requested` with findings. Never edits. |
| `review` skill | Runs the reviewer on a branch, commit range or PR, and reports the verdict. |
| Python hook runtime | One launcher, one shared library, a `unittest` suite. Replaces the bash-only path for every hook. |
| Guard hooks | Plugin-wide rules that hold in every session where devflow is enabled. |
| `.claude/devflow.json` | Per-project settings the hooks and agents read. |

This spec carries the foundation because the reviewer is the smallest workflow that needs all of
it: an agent, a rule it must not break (read-only), and tests proving the rule holds.

## Live test on Inverso

Inverso is the test bed for all four releases, the way a failing test drives code: each release is
**accepted only when it has been used on Inverso for real**, and what goes wrong there becomes the
next change to the skill — before devflow decides what it keeps.

| Release | Accepted when, on Inverso |
|---|---|
| 0.13.0 `review` | it reviews the next Inverso task and its verdict matches the project reviewer's on the same commit; every guard rule has fired at least once in a real session |
| 0.14.0 `fix-bug` | an Inverso bug goes from `docs/issues/` to merged through it |
| 0.15.0 `implement` | an Inverso milestone (M2) is built with it instead of the project's own `build-milestone` |
| 0.16.0 `write-specs` | a real brainstorm for an Inverso feature becomes specs that `implement` builds |

Inverso's own `.claude/` agents, skill and hooks stay in place until the release that replaces them
has passed; then they are removed from Inverso in one commit. While both run, Inverso's
`.claude/devflow.json` lists no `apps`, so its test suites are not run twice on every commit (Inverso's
own pre-commit hook still runs them).

## Why prose is not enough

The motivating failure is the evidence skill: it sometimes reads only part of the commit range,
sometimes creates only some of the documents, and is inconsistent between sessions. Each of those
is a **mechanical step left to judgement**. Inverso showed the same pattern: implementers skipped
three planned items in T13, an agent ran `taskkill /IM node.exe`, and an orchestrator nearly ran
`docker compose down -v` on the shared database.

The vendor digest already says it (`docs/skill-authoring.md`, *Body content*): a rule that must
hold every time belongs in a hook, not in prose. This design applies it:

- **Must hold every time** → a hook, with a test proving it blocks and a test proving it allows.
- **Mechanical but multi-step** (a list of commits, the set of documents to create) → a script the
  skill executes, whose output the model acts on; the script is tested.
- **Judgement** → skill and agent prose.

## The Python hook runtime

### Why Python, not bash

- The current hook is bash behind a cmd/bash polyglot (D-005). Its JSON is built with `printf`
  and no escaping (`CLAUDE.md`, *Hook gotchas*), and it is not tested.
- Enforcement hooks parse commands, resolve paths across worktrees and run test suites. That is
  painful and untestable in bash; Inverso's equivalents are 6 Python files with a 37-test suite.
- Python's standard library covers everything needed (`json`, `re`, `shlex`, `subprocess`, `os`,
  `pathlib`, `hashlib`, `unittest`), so the repo still has **no dependencies** — only an interpreter.

### Standard library only

**The hooks, the scripts and their tests import nothing outside Python's standard library. Nothing
is ever downloaded with pip, uv or any other tool.** Tests use `unittest`, not pytest.

Enforced, not promised: a test walks every `.py` file under `hooks/`, `skills/` and `tests/`, parses
its imports with `ast`, and fails on any top-level module that is neither in
`sys.stdlib_module_names` nor one of devflow's own modules. `sys.stdlib_module_names` exists from
Python 3.10, which is one reason 3.10 is the floor.

### Python is a checked requirement: detect, ask, install visibly

devflow requires **Python ≥ 3.10** (a floor, not an exact version: 3.11–3.14 all qualify).

1. **Detect.** The session-start hook runs in `cmd` on Windows and `sh` elsewhere (the polyglot
   wrapper), so it needs no Python. It looks for `py -3`, `python3`, `python` and checks the version.
2. **Ask.** If none qualifies, its injected context tells Claude to tell the developer, at the start
   of the session, what is missing and the install command for their platform — and to wait.
3. **Install visibly.** Only after the developer says yes, Claude runs that command as an ordinary
   tool call the developer sees and approves: `winget install Python.Python.3.14` (Windows, per-user
   scope where the package allows it `[VERIFY]`), `brew install python@3.14` (macOS, when Homebrew is
   present), the distribution's package manager on Linux (needs `sudo`, so the developer may run it
   themselves with `!`). No hook installs anything itself: a hook cannot answer a UAC or `sudo` prompt,
   and installing software without asking is what managed settings exist to block.
4. **Until then, guards block.** Every guard hook fails closed with the same message, so nothing runs
   unguarded while Python is missing.

### Launch

`[VERIFY]` Claude Code can spawn a hook with no shell (`command` resolved on `PATH`, `args` passed
directly). Which Python command exists differs per machine: `py` (Windows launcher), `python3`
(macOS/Linux), `python`. The docs say nothing about this.

Design: every hook entry runs one launcher, `hooks/run.py`, through the interpreter found by a
small polyglot wrapper (the D-005 technique kept, retargeted from bash to Python):

1. The wrapper tries `py -3`, then `python3`, then `python`, and requires ≥ 3.10.
2. It runs `hooks/run.py <hook-name>`, which imports the hook module and calls it.
3. **No interpreter found:** for a guard hook, print the reason and the install command and **block**
   (exit 2). For the session-start hook, emit the *detect → ask* context above instead of its normal
   pointer. D-005's silent exit 0 is gone from both: it was right for optional context and wrong for
   anything load-bearing, and a missing requirement is now something the developer is told about.
   Claude Code 2.1.299 also changed failing guard hooks to block.

**Probe before building (task 1):** on Windows (Git Bash present, and absent), macOS and Linux,
confirm which form Claude Code actually spawns, that `CLAUDE_PLUGIN_ROOT` reaches the hook, what
`agent_type` holds in the main session and in a plugin agent, and that `ask` reaches the user.
Record the results as fixtures; the hook tests replay them.

### Layout

```
hooks/
  hooks.json            every registration
  run-hook.cmd          polyglot: find Python, run run.py (replaces the bash dispatch)
  run.py                entry point: run.py <hook-name>
  devflow_hooks/
    lib.py              read_event, allow, deny, ask, agent_of, git_root, repo_relative, config
    session_start.py    port of hooks/session-start; same output, now tested
    guard_bash.py       command rules
    guard_paths.py      file-write rules
    pre_commit.py       skipped-test check + configured test suites
tests/
  test_hooks.py         unittest; feeds each hook a JSON event, checks the decision
  fixtures/             events captured in the probe
```

`hooks/session-start` (bash) is deleted; its behaviour moves to `session_start.py` unchanged and
gains the test that it emits exactly one context field.

### Decisions are JSON, not exit codes

Hooks exit 0 and print `hookSpecificOutput.permissionDecision` (`deny` / `ask` / `allow`) with a
reason. Exit 2 is kept only for the wrapper's "no Python" path. Reason: `ask` has no exit-code form,
and one output style is one thing to test.

## Who is who

Plugin agents are named `devflow:<name>`, and that is what a hook sees in `agent_type`. Plugin agents
cannot carry their own hooks or permission mode (ignored for security), so **every rule lives in the
plugin's `hooks/hooks.json` and branches on `agent_type`**:

| `agent_type` | Treated as |
|---|---|
| absent `[VERIFY in probe]` | main session — the developer's own session |
| `devflow:reviewer`, `devflow:implementer`, `devflow:planner` | that devflow agent |
| anything else | an agent devflow does not own: only the rules marked *everyone* apply |

## Guard rules

Plugin hooks fire in **every session where devflow is enabled**, every project. That is the
intended scope: these are devflow's rules, and a rule that annoys can be removed later.

| Rule | Main session | Any agent | devflow agents |
|---|---|---|---|
| `git push` (any form: `git -C x push`, after `;`/`&&`/`|`, in `{ }`) | **ask** the developer | **deny** | deny |
| `docker compose down -v` / `--volumes` | deny | deny | deny |
| Kill processes by image name (`taskkill /IM`, `pkill -f node`, `Stop-Process -Name`) | — | deny | deny |
| `--no-verify` on git | deny | deny | deny |
| Edit `.claude/` (agents, skills, hooks, settings, `devflow.json`) | — | deny | deny |

Per devflow agent (this release ships only the reviewer; the rows for the others land with their
specs but are listed here so the table is the one place the rules live):

| Agent | Commands | Files |
|---|---|---|
| `reviewer` | read-only git (`log`, `diff`, `show`, `status`, `switch --detach`), test commands, locked installs (`npm ci`, `uv sync`) in its own worktree. No `add/commit/merge/rebase/reset/...`, no file-changing shell. | none |
| `implementer` (0.14.0) | no `merge/rebase/cherry-pick`, `reset --hard`, switching to the default branch, `branch -D` | not the protected paths |
| `planner` (0.15.0) | read-only | only its plan file |

Command matching follows the lesson from Inverso's push hook: Claude Code's `if` filter is
best-effort and fires on commands it cannot split, so **the script checks the command itself**, and
hooks register without `if`. A command counts only where it starts a statement, so a commit message
mentioning `git push` does not trigger it.

## Pre-commit gate

On `git commit`, in every session:

1. No skipped or focused tests in the added lines (`.skip`, `.only`, `xit`, `@pytest.mark.skip`,
   `xfail`, `@unittest.skip`, …).
2. For each configured app folder the commit touches, its test command passes.

No `apps` in the config → only check 1 runs. Projects opt into the slow part.

## `.claude/devflow.json`

```json
{
  "default_branch": "main",
  "protected_paths": ["docs/specs/", "docs/plans/", "docs/issues/", "docs/design/"],
  "apps": {
    "web":    { "test": "npm test",          "install": "npm ci" },
    "worker": { "test": "uv run pytest -q",  "install": "uv sync" }
  },
  "rule_id_pattern": "[A-Z]+-\\d{3}",
  "specs_dir": "docs/specs",
  "plans_dir": "docs/plans"
}
```

- Lives under `.claude/`, so the "agents never edit `.claude/`" rule protects it.
- Every key optional; missing file = defaults (`main`, no protected paths, no apps).
- devflow never creates it unasked: `review` proposes it on first use and waits (the plugin rule:
  nothing written into a project that has not agreed to it).

## The reviewer agent

`agents/reviewer.md`, from Inverso's reviewer with its M1 lessons, generalised:

- **Inputs:** what to review (task in a plan, bug report, or just a range) and the implementer's
  report if there is one.
- **Process:** read the task or report, every rule it names, the diff; re-run the tests; never
  trust the report's numbers.
- **Checklist:** rules really tested · **tests can fail** (break the behaviour, the test goes red) ·
  **whole task done** (every planned item and note, or listed under `NOT DONE`) · tests not weakened
  · scope · spec match · security · quality.
- **May not approve** if it could not run the tests; it says why.
- **Output:** the fixed `VERDICT` block.
- `model: opus`, `isolation: worktree`, `tools: Read, Grep, Glob, Bash`.

Project-specific checks (Inverso's design-system and privacy rows) do not ship. A project adds them
in its own instructions; the reviewer reads `CLAUDE.md` like any session.

## The `review` skill

Triggered by: "review this branch/PR/commit", a finished change before merge. Steps:

1. Resolve the target to a commit range. Check Docker/tools needed by the configured test commands
   are running, not just installed.
2. Dispatch `devflow:reviewer` with the range and any plan task or report.
3. Report the verdict to the user as a short table: what was checked, what was run, findings by
   severity. Never merge, never fix.

**Trigger collision:** Claude Code ships a built-in `code-review` skill with an overlapping
description. `review`'s description must name what differs — a verdict against a plan or spec, from
an isolated agent that re-runs the tests — or the two compete. Covered by an eval case.

## Testing and CI

- `python -m unittest discover -s tests` — every hook: one test that it blocks, one that it allows,
  for the main session and for agents; fixtures from the probe.
- `claude plugin validate --strict` — manifests, agent and skill frontmatter.
- `claude plugin eval` — trigger cases for `review` vs the built-in `code-review`. Billed, so run on
  demand, not on every push.
- GitHub Actions matrix: `windows-latest`, `ubuntu-latest`, `macos-latest` for the unittest suite and
  validate.

This ends the "no test suite" property stated in `CLAUDE.md`; that line changes in the same release.

## Decisions to record when implemented

- **D-027** — Hooks are Python ≥ 3.10, standard library only (enforced by a test), with a
  `unittest` suite; Python is detected at session start and installed only after the developer
  agrees. *Amends the "no test suite" property.*
- **D-028** — Enforcement hooks fail closed and are plugin-wide. *Supersedes D-005* for anything
  load-bearing; the polyglot wrapper survives, retargeted to Python.
- **D-029** — `git push` asks the developer and is denied to every agent.
- **D-030** — Workflows ship as plugin agents plus skills, one spec and one release each.

## Not in this release

- Issues, the implementer, the merge procedure and `fix-bug` → `2026-10-14-fix-bug-design.md` (0.14.0).
- The planner, batches and `implement`; removal of `mvp` and `project-specs` →
  `2026-10-14-implement-design.md` (0.15.0).
- Turning a feature description or brainstorming notes into rule-ID specs →
  `2026-10-14-write-specs-design.md` (0.16.0).
- A QA agent and skill — designed only after `implement` has been used on Inverso.
- Scripting the evidence skill's mechanical steps (commit replay, document set) → proposed as a
  fourth spec; it reuses this runtime and test suite.

## Open questions

1. **`ask` in the main session only.** If the probe shows `agent_type` is present in the main session
   in some modes, the push rule needs another signal. Answer comes from the probe.
2. **Hooks in other projects.** Every devflow project gets the guard rules, including `.claude/`
   being read-only to agents. Confirmed as intended (2026-10-14), recorded here so D-028 cites it.
