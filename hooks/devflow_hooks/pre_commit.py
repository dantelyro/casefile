"""PreToolUse on Bash and PowerShell: checks before any `git commit`, in every session.

Port of Inverso's pre_commit.py (TEST-001, TEST-002):
1. No skipped or focused tests in the added lines of test files.
2. The design check on the added lines of UI files, so a file written outside Claude Code's edit
   tools is caught too.
3. The test command of every configured app the commit touches passes, and its lint command when
   it has one.

A commit only counts where `git commit` starts a statement (guard_bash's parsing). With no `apps`
configured, step 3 runs nothing: projects opt into the slow part.
"""

import os
import re
import shlex
import shutil
import subprocess

from devflow_hooks import lib
from devflow_hooks.design_check import Checker, DesignSystemError
from devflow_hooks.guard_bash import _short_flags, statements

SKIP_MARKERS = re.compile(
    r"\b(it|test|describe)\.(skip|only|todo)\b"     # Vitest / Jest / Playwright
    r"|\bx(it|describe|test)\s*\("                   # xit(, xdescribe(
    r"|\bf(it|describe)\s*\("                        # fit(, fdescribe(  (focused)
    r"|@pytest\.mark\.(skip|skipif|xfail)\b"         # pytest markers
    r"|\bpytest\.(skip|xfail)\s*\("                  # pytest calls
    r"|@unittest\.(skip|expectedFailure)\b"          # skipIf/skipUnless: platform conditions, allowed
)
TEST_FILE = re.compile(r"(^|/)(tests?|e2e)/|\.(test|spec)\.([cm]?[jt]s|[jt]sx)$|(^|/)test_[^/]*\.py$|_test\.py$")
SUITE_TIMEOUT = 840  # the hook is registered with 900 s


def _commit(command: str):
    """The `git commit` statement in this command, or None."""
    for s in statements(command):
        sub, args = s.git()
        if sub == "commit":
            return s, args
    return None


def _git(root: str, *args: str) -> str:
    out = subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                         encoding="utf-8", errors="replace")
    return out.stdout


def _added_lines(diff: str) -> dict[str, list[str]]:
    added: dict[str, list[str]] = {}
    current = None
    for line in diff.splitlines():
        if line.startswith("+++ "):
            current = line[6:] if line.startswith("+++ b/") else None
        elif line.startswith("+") and current:
            added.setdefault(current, []).append(line[1:])
    return added


def _run(command: str, cwd: str) -> tuple[int, str]:
    # Through the shell, which finds npm.cmd on Windows and npm elsewhere.
    out = subprocess.run(command, cwd=cwd, shell=True, capture_output=True, text=True,
                         encoding="utf-8", errors="replace", timeout=SUITE_TIMEOUT)
    return out.returncode, out.stdout + out.stderr


def main(event: dict) -> None:
    found = _commit((event.get("tool_input") or {}).get("command") or "")
    if not found:
        lib.allow()
    statement, args = found
    cwd = event.get("cwd") or os.getcwd()
    if "-C" in statement.args:
        i = statement.args.index("-C")
        if i + 1 < len(statement.args):
            cwd = os.path.join(cwd, statement.value(statement.args[i + 1]))
    root = lib.git_root(cwd)
    if not root:
        lib.allow()

    # `git commit -a` stages tracked changes at commit time, so compare with HEAD.
    commit_all = "--all" in args or "a" in _short_flags(args)
    target = ["HEAD"] if commit_all else ["--cached"]
    files = [f for f in _git(root, "diff", *target, "--name-only").splitlines() if f]
    if not files:
        lib.allow()
    added = _added_lines(_git(root, "diff", *target, "--unified=0", "--", *files))
    cfg = lib.config({"cwd": root})

    exempt = tuple(cfg["allow_skip_markers_in"])
    offenders = [f"{path}: {line.strip()[:120]}"
                 for path, lines in added.items()
                 if TEST_FILE.search(path) and not (exempt and path.startswith(exempt))
                 for line in lines if SKIP_MARKERS.search(line)]
    if offenders:
        lib.deny("skipped or focused tests can't be committed; make them pass or remove them:\n  "
                 + "\n  ".join(offenders[:10]))

    try:
        checker = Checker.for_event({"cwd": root})
    except DesignSystemError as e:
        lib.deny(f"{e}, so the commit's UI files cannot be checked.")
    if checker:
        problems = []
        for path in files:
            problems += checker.check_path(path) + checker.check_text(path, "\n".join(added.get(path, [])))
        if problems:
            lib.deny(f"the commit invents styles outside the design system (`{checker.tokens_path}`):\n  "
                     + "\n  ".join(problems[:15]))

    for name, app in cfg["apps"].items():
        folder = (app.get("path") or name).strip("/")
        whole_repo = folder in ("", ".")  # "path": "." — the repository is the app
        if not (whole_repo or any(f.startswith(folder + "/") for f in files)):
            continue
        # `lint` is optional: the developer may decline a linter; `test` is the mandatory one (D-042)
        for kind, label, fails in (("test", "tests", "fail"), ("lint", "lint", "fails")):
            command = app.get(kind)
            if not command:
                continue
            tool = shlex.split(command, posix=os.name != "nt")[0]
            if shutil.which(tool) is None:
                lib.deny(f"`{tool}` isn't on PATH, so the {name} {label} did not run (no failure was seen). "
                         f"Make `{tool}` available to this session and retry the commit.")
            try:
                code, output = _run(command, root if whole_repo else os.path.join(root, *folder.split("/")))
            except subprocess.TimeoutExpired:
                lib.deny(f"the {name} {label} took longer than {SUITE_TIMEOUT // 60} minutes; commit refused.")
            if code != 0:
                tail = "\n".join(output.strip().splitlines()[-30:])
                lib.deny(f"the {name} {label} {fails} (`{command}`), so the commit is refused. Last lines:\n{tail}")

    lib.allow()
