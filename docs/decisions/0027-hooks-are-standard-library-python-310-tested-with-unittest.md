# D-027 — Hooks are standard-library Python ≥ 3.10, tested with unittest

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session. The 0.13.0 spec
(`docs/specs/history/2026-10-14-review-design.md`) was approved on 2026-10-14 with Python, the standard
library only and no downloads; asked again on 2026-10-15 whether sh + jq would be simpler: "keep
python".
**Implemented by:** `b71c36c` — 2026-10-15 (runtime and library), with each hook from `65adde2` to
`d49a8f9`.

**Context:** devflow's enforcement moves from prose into hooks (0.13.0 spec, *Why prose is not
enough*). The guards parse shell commands into statements, map file paths across worktrees and
Windows/Unix separators, read a design system's `tokens.json`, compare added lines of a commit and
run test suites — and each rule needs a test that it blocks and one that it allows. The only hook
so far was a bash script whose JSON was built with `printf` and never tested.

**Options:** (a) bash (or sh) with `jq` for the JSON; (b) Python, standard library only; (c) Node,
which Claude Code itself ships on.

**Decision:** (b), at **Python ≥ 3.10** (`sys.stdlib_module_names`, used by the import test, starts
there; `X | None` annotations need it). Nothing is ever downloaded — no pip, no uv; tests use
`unittest`, and a test fails on any import outside the standard library. A missing Python is
detected by the `sh` starter, which tells Claude to tell the developer the install command and
wait; no hook installs anything. The pilot project's hooks, which this release ports, were already Python.

**Trade-offs:** Python is a requirement a user may have to install (jq would be one too: it is not
in Git for Windows and not reliably on macOS or Linux). The starter has to find whichever Python
command a machine has (`py -3`, `python3`, `python`), and on Windows `python3` can be the
Microsoft Store stub, so every candidate is version-checked. (c) was not pursued: the pilot project's hooks,
the code being ported, are Python, and whether every Claude Code install puts `node` on `PATH` was
never checked. The "no test suite" property in `CLAUDE.md` ends.
