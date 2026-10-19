# 0.13.0 — `review`, the Python hooks and the design check — implementation plan

**Spec:** `docs/specs/history/2026-10-14-review-design.md` (approved 2026-10-14, design check added 2026-10-15).
**Starts from:** `47c0d4e` on `main`, version `0.12.0`.
**Ships as:** `0.13.0`.

**Goal:** devflow gets its first agent (`devflow:reviewer`), its first workflow skill (`review`), and
enforcement: every hook the pilot project uses, rewritten as tested, standard-library Python that works in any
project. Accepted only after it has worked on the pilot project for real (task 14).

**How this plan is run:** in a devflow session, by the main session, one task at a time, test first.
Each task ends with its tests green, a summary shown to the developer, and a commit after their yes.
Never push. Tasks 1 and 14 need the developer at the keyboard.

## Global constraints

Every task includes these.

- **Standard library only, Python ≥ 3.10.** No pip, no uv, no pytest. Tests are `unittest`. Task 2's
  import test enforces it from then on.
- **Hook decisions are JSON** (`permissionDecision`: `deny` / `ask` / `allow`, with a reason), exit 0.
  Exit 2 only for "no Python found".
- **Guards fail closed.** A hook that crashes or cannot read its input blocks; it never lets the call
  through.
- **Every rule has a test that it blocks and a test that it allows**, for the main session and for
  agents.
- **No `if` filters in `hooks.json`.** Each script checks the command itself (the pilot project `437d754`).
- **Commands count only where they start a statement**, so a commit message mentioning `git push`
  does not trigger a rule.
- **Conventional commits** (D-007): `feat:` for hooks, agent and skill; `test:`, `docs:`, `ci:`,
  `chore:` otherwise. No co-author lines.
- **State each rule once** (D-008): the guard table lives in the spec and in the code, nowhere else.
- **Nothing written into a project that has not agreed to it.** No hook creates a file in the project.

## Files

| Path | Task | What |
|---|---|---|
| `docs/skill-authoring.md` | 0 | Brought to the running Claude Code version |
| `probe/` (deleted after task 1) | 1 | Throwaway plugin that records what hooks receive |
| `tests/fixtures/*.json` | 1 | Events captured in the probe |
| `hooks/run-hook.cmd` | 2 | Polyglot wrapper, retargeted from bash to Python |
| `hooks/run.py` | 2 | `run.py <hook-name>` |
| `hooks/devflow_hooks/lib.py` | 2 | `read_event`, `allow`, `deny`, `ask`, `agent_of`, `git_root`, `repo_relative`, `config` |
| `hooks/devflow_hooks/session_start.py` | 3 | Port of `hooks/session-start`; `hooks/session-start` deleted |
| `hooks/devflow_hooks/guard_bash.py` | 4 | Command rules |
| `hooks/devflow_hooks/guard_paths.py` | 5 | File-write rules |
| `hooks/devflow_hooks/design_check.py` | 6 | Design-system rules |
| `hooks/devflow_hooks/pre_commit.py` | 7 | Skipped tests, design check on added lines, app test suites |
| `hooks/hooks.json` | 8 | Every registration |
| `agents/reviewer.md` | 9 | `devflow:reviewer` |
| `skills/review/SKILL.md` | 10 | The `review` skill |
| `evals/` | 10 | Trigger cases, `review` vs built-in `code-review` |
| `tests/test_*.py` | 2–8 | `python -m unittest discover -s tests` |
| `.github/workflows/test.yml` | 11 | Windows, Ubuntu, macOS |
| `CLAUDE.md`, `README.md`, manifests, `docs/decisions/` | 12–13 | Docs, decisions, version |

---

## Task 0 — Bring `docs/skill-authoring.md` to the running version

`CLAUDE.md` requires it at session start, and it is behind: watermark `2.1.295`, running `2.1.300`.
This release depends on hook behaviour, so it goes first.

- [x] `claude --version`; read the changelog entries from 2.1.296 to the running version (2.1.297 and
      2.1.298 were missing from the copy read on 2026-10-14; fetch them).
- [x] Re-fetch the hooks and plugins pages the file cites. Record anything about plugin hooks,
      `agent_type`, `permissionDecision: "ask"`, exec-form commands, failing hooks (`onFailure`).
- [x] Update the file and move its watermark, even if nothing changed.
- [x] Tell the developer anything that changes this plan before starting task 1.
- [x] Also fix the stale path in `CLAUDE.md` (`D:\projects\personal\devflow` →
      `C:\Users\beyon\projects\devflow`).
- Commit: `docs: verify skill-authoring against <version>`.

## Task 1 — Probe: how Claude Code really runs plugin hooks here

Everything marked `[VERIFY]` in the spec is answered by watching a real session, not by reading.

- [x] Build `probe/`: a minimal plugin with one PreToolUse hook (matcher `Bash|PowerShell|Edit|Write`),
      one SessionStart hook and one agent (`probe/agents/prober.md`). The hook appends the raw event
      JSON and its environment (`CLAUDE_PLUGIN_ROOT`, `PATH`) to a log file outside the repo, and
      returns `ask` for any command containing `probe-ask`.
- [x] Load it in a fresh session with `claude --plugin-dir probe` (documented in the CLI reference). The developer runs these, and Claude records what happens:

  | # | Question | How |
  |---|---|---|
  | 1 | Does `run-hook.cmd` in shell form run under Git Bash, and under PowerShell with Git Bash hidden from `PATH`? (Exec form cannot spawn a `.cmd` on Windows, per the docs.) | Log the shell and `sys.argv` |
  | 2 | Which Python command is found (`py -3`, `python3`, `python`) and its version | The hook logs `sys.executable` |
  | 3 | Does `CLAUDE_PLUGIN_ROOT` reach the hook? | Logged env |
  | 4 | What is `agent_type` in the main session? In `probe:prober`? In a built-in agent (`Explore`)? | Run one command from each |
  | 5 | Does `ask` reach the developer in the main session? What happens in a subagent? | `echo probe-ask` from each |
  | 6 | What `tool_name` and `tool_input` do Bash and PowerShell send? Edit and Write? | Logged events |
  | 7 | Does the SessionStart hook fire on `startup`, `clear` and `compact`? | Logged events |
  | 8 | With `onFailure: "block"`, is the call refused when the hook crashes (exit 1) and when it times out? Without it, does the call go through? | A command containing `probe-crash` / `probe-sleep` |

- [x] Save one event per case as `tests/fixtures/<case>.json` (strip anything personal: paths become
      `<root>`). Write the answers into the spec's `[VERIFY]` spots, and resolve its open question 1.
- [x] Delete `probe/`.
- **If the answers change the design** (for example, `ask` does not reach the developer, or
  `agent_type` is present in the main session): stop and show the developer before task 2.
- Commit: `test: capture hook events from a live probe`, plus `docs:` for the spec update.

## Task 2 — Python runtime and the library

- [x] Tests first (`tests/test_lib.py`, `tests/test_stdlib_only.py`):
  - `read_event` on each fixture; bad JSON → the hook denies (fails closed).
  - `deny`/`ask`/`allow` print the JSON shape from task 1, exit 0.
  - `agent_of`: main session → `None`; plugin agent → `devflow:reviewer`; from fixtures.
  - `git_root` and `repo_relative` inside a worktree (`.claude/worktrees/x/web/a.ts` → `web/a.ts`).
  - `config`: no file → defaults; partial file → defaults filled; invalid JSON → deny with the file
    named.
  - Import test: every `.py` under `hooks/`, `skills/`, `tests/` imports only
    `sys.stdlib_module_names` or devflow's own modules.
- [x] `hooks/devflow_hooks/lib.py`, from the pilot project's `_hooklib.py` plus `ask` and `config`.
- [x] `hooks/run.py`: imports `devflow_hooks.<name>` and runs it; any exception → deny with the
      error (fails closed), except for `session_start`, which never blocks.
- [x] `hooks/run-hook.cmd`: the launch form task 1 chose. Finds `py -3`, `python3`, `python`, requires
      ≥ 3.10. None found: guard hooks print the install command (`winget install Python.Python.3.14`,
      `brew install python@3.14`, the Linux package manager) and exit 2; `session-start` emits the
      *detect → ask* context instead.
- [x] Test the wrapper's no-Python path by running it with an empty `PATH` (both Windows cmd and sh in
      CI).
- Commit: `feat: python hook runtime, fails closed`.

## Task 3 — Session start in Python

- [x] Test: output equals today's `hooks/session-start` output, byte for byte after JSON parsing,
      under `CLAUDE_PLUGIN_ROOT` (nested form) and without it (top-level form); exactly one context
      field.
- [x] `session_start.py`; delete `hooks/session-start`. The `printf` escaping gotcha in `CLAUDE.md`
      goes away with it.
- Commit: `feat: session-start hook in python`.

## Task 4 — Command guard

Port of the pilot project's `block_push.py` and `guard_bash.py`, with their tests.

- [x] Tests, for each row of the spec's guard table, main session / other agent / devflow agent:
  - `git push` in every form (`git -C x push`, after `;` `&&` `|`, inside `{ }`, PowerShell) → ask in
    main, deny in agents. `git commit -m "… git push …"` → allowed.
  - `docker compose down -v`, `--volumes` → deny for everyone. `docker compose down` → allowed.
  - `--no-verify` on any git command → deny for everyone.
  - `taskkill /IM`, `pkill -f`, `Stop-Process -Name` → deny for agents, allowed in main.
  - `devflow:reviewer`: `git add/commit/merge/rebase/reset/stash/branch -d`, `rm`, redirects that write
    files → deny; `git log/diff/show/status`, `git switch --detach`, `npm ci`, `uv sync`, test commands
    → allowed.
  - Every reason tells the reader what to do instead ("commit locally and report back; the developer
    pushes").
- [x] `guard_bash.py`. The implementer and planner rows are written as data now but tested when
      their agents ship (0.14.0, 0.15.0).
- Commit: `feat: command guard for push, volumes, no-verify, kills and the reviewer`.

## Task 5 — File guard

Port of the pilot project's `guard_paths.py`.

- [x] Tests: any agent editing `.claude/…` → deny; main session → allowed. `devflow:reviewer` writing
      any file → deny. Protected paths from config (`docs/product/x.md`) → deny for devflow agents,
      allowed in main. Paths inside a worktree resolve to the repo-relative path first.
- [x] `guard_paths.py`.
- Commit: `feat: file guard for .claude, protected paths and the reviewer`.

## Task 6 — Design check

Port of the pilot project's `design_lint.py` + `design_rules.py`, driven by config instead of the pilot project's paths.

- [x] Fixture `tests/fixtures/design/tokens.json`: a small design system in the claude.ai Design System
      format (a few colours, spacing steps, radii, shadows, type styles, two families), plus a
      `components/` folder with two components.
- [x] Tests, built from the pilot project's blocked and allowed examples:
  - Raw colours (hex, `rgb()`, `oklch()`, named), raw lengths except `1px`, `font-family` → deny,
    except in `raw_values_allowed` files.
  - Tailwind (with `classes: "tailwind"`): arbitrary values, colour / spacing / radius / shadow /
    text-size / weight / family classes not in the tokens → deny; token classes → allowed. Without
    `classes`, class rules do not run.
  - Forbidden imports from config → deny.
  - A file in `components_dir` whose name is not a design-system component → deny.
  - Not a UI file, a test file, or no `tokens.json` → allowed without reading anything.
  - Main session is checked too.
  - The reason names the token to use, and says to extend the design system if it lacks one.
- [x] `design_check.py`, exposing `check_path` and `check_text` for task 7.
- [x] Run it over the pilot project's `web/` with the pilot project's settings (task 14's `devflow.json`): it must report
      exactly what the pilot project's own `design_lint.py` reports on the same files (today: nothing).
- Commit: `feat: design check against the project's design system`.

## Task 7 — Pre-commit gate

Port of the pilot project's `pre_commit.py`.

- [x] Tests (in a temporary git repo built by the test):
  - Added `.skip`, `.only`, `xit`, `@pytest.mark.skip`, `xfail`, `@unittest.skip` → deny; the same text
    in removed lines or in a non-test file → allowed.
  - Added UI lines that break the design check → deny.
  - A configured app touched and its test command fails → deny with the tail of its output; passes →
    allowed; app not touched → not run. No `apps` → no suite runs.
  - Only `git commit` starting a statement triggers it.
- [x] `pre_commit.py`.
- Commit: `feat: pre-commit gate for skipped tests, design and app suites`.

## Task 8 — Register the hooks

- [x] `hooks/hooks.json`: SessionStart (`startup|clear|compact`) → `session-start`; PreToolUse
      `Bash|PowerShell` → `guard_bash`, `pre_commit` (timeout 900, status message); PreToolUse
      `Edit|Write|NotebookEdit` → `guard_paths`, `design_check`. No `if`. Every guard and `pre_commit`
      registered with `onFailure: "block"`; `session-start` without it, since it never blocks.
- [x] Test: every registered name has a module, and every module is registered.
- [x] `claude plugin validate` passes.
- [x] Smoke test in a live session with the working copy loaded: a push asks, `down -v` is denied.
- Commit: `feat: register the guard hooks plugin-wide`.

## Task 9 — The reviewer agent

- [x] `agents/reviewer.md`, from the pilot project's `.claude/agents/reviewer.md` with its M1 lessons, generalised
      (no the pilot project names, paths or rules): inputs (plan task, issue, or a commit range; the
      implementer's report if any); process (read the task and every rule it names, the diff; re-run
      the tests with the configured commands; never trust the report's numbers); checklist (rules
      really tested · tests can fail · whole task done, every planned item and note or `NOT DONE` ·
      tests not weakened · scope · spec match · security · quality); may not approve if it could not
      run the tests; the fixed `VERDICT` block.
- [x] Frontmatter: `model: opus`, `isolation: worktree`, `tools: Read, Grep, Glob, Bash`.
- [x] Check in a live session: `devflow:reviewer` appears, its `agent_type` is what task 1 recorded,
      and task 4's reviewer rules block it.
- Commit: `feat: reviewer agent`.

## Task 10 — The `review` skill

- [x] `skills/review/SKILL.md`: resolve the target to a commit range; check that the tools the test
      commands need are running, not just installed; dispatch `devflow:reviewer`; report the verdict as
      a short table (checked, run, findings by severity). Never merges, never fixes. First use in a
      project without `.claude/devflow.json`: propose one and wait.
- [x] Description names what differs from the built-in `code-review`: a verdict against a plan or spec,
      from an isolated agent that re-runs the tests.
- [x] Eval cases in `evals/`: prompts that must trigger `review`, prompts that must trigger
      `code-review` instead. Run `claude plugin eval` once (billed; on demand, not in CI).
- Commit: `feat: review skill`.

## Task 11 — CI

- [x] `.github/workflows/test.yml`: `windows-latest`, `ubuntu-latest`, `macos-latest`; Python 3.10 and
      the newest; `python -m unittest discover -s tests`; `claude plugin validate` `[VERIFY]` that the
      CLI installs in CI without a login.
- Commit: `ci: run the hook tests on three platforms`.

## Task 12 — Decisions

Per `skills/evidence-based-decisions/references/decision-log.md`, `Decided by` from the developer's
words in the 2026-10-14 session.

- [x] D-027 Python ≥ 3.10, standard library only, `unittest`, installed only after the developer
      agrees. D-028 Enforcement hooks fail closed and are plugin-wide, the design check included;
      supersedes D-005 for anything load-bearing. D-029 `git push` asks the developer and is denied to
      every agent. D-030 Workflows ship as plugin agents plus skills, one spec and one release each.
- [x] D-005's status line; the index.
- Commit: `docs: record D-027 to D-030`.

## Task 13 — Docs and version

- [x] `CLAUDE.md`: the repo now has a test suite (how to run it); hooks are Python (the *Hook gotchas*
      section rewritten for the new runtime); three skills and one agent; watermark moved.
- [x] `README.md`: the `review` skill, the guard rules in one line each with a pointer to the spec,
      `.claude/devflow.json`, the Python requirement.
- [x] `plugin.json` and `marketplace.json`: the same new `description`; `version` → `0.13.0`.
- Commit: `feat: ship 0.13.0` (the version bump is the shipped change).

## Task 14 — Live test on the pilot project

0.13.0 is accepted only when all of these hold. Whatever goes wrong becomes the next devflow change.

- [ ] Install devflow 0.13.0 in the pilot project. Add the pilot project's `.claude/devflow.json` (with the developer's
      yes): `protected_paths` as the pilot project's hooks have them, **no `apps`** (the pilot project's own pre-commit
      still runs the suites), and `design`: `tokens: docs/design/tokens.json`, `ui_paths: ["web/"]`,
      `components_dir: web/components/ui/`, `classes: tailwind`, the pilot project's raw-value exceptions and
      forbidden icon libraries.
- [ ] Replace the pilot project's hooks **one at a time**: turn one off in `.claude/settings.json`, show that
      devflow's equivalent blocks the same things in a real session, then delete the pilot project hook and
      its tests:

  | The pilot project hook | devflow hook | Shown by |
  |---|---|---|
  | `block_push.py` | `guard_bash` | a push in the main session asks; an agent's push is denied |
  | `guard_bash.py` | `guard_bash` | `down -v` denied; an agent's `taskkill /IM` denied |
  | `guard_paths.py` | `guard_paths` | an agent's edit to `.claude/` and to `docs/specs/` denied |
  | `design_lint.py` + `design_rules.py` | `design_check` | a raw hex colour in `web/` denied |
  | `pre_commit.py` | `pre_commit` | an added `.only` denied; then `apps` added to the pilot project's config and the suites run |

  the pilot project's "no AI search in the MVP" rule stays as a small the pilot project hook.
- [ ] `devflow:reviewer` reviews an already-reviewed the pilot project commit (one of M1's) and reaches the same
      verdict as the pilot project's reviewer did.
- [ ] Every guard rule and the design check have fired at least once in a real session.
- [ ] Record what went wrong; open the follow-ups before 0.14.0.

## Not in this plan

The implementer, issues and `fix-bug` (0.14.0); the planner and `implement` (0.15.0); `write-specs`
(0.16.0); scripting the evidence skill's steps (a later spec).
