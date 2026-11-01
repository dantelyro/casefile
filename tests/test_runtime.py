"""The launcher (run.py) and the starter (run-hook): guards fail closed."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import types

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS))

import run  # needs HOOKS on sys.path first

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
FIXTURE = (FIXTURES / "bash_main.json").read_text(encoding="utf-8")
SESSION_START = (FIXTURES / "session_start_startup.json").read_text(encoding="utf-8")


def fake_importer(**modules):
    def importer(name):
        short = name.rsplit(".", 1)[-1]
        if short not in modules:
            raise ModuleNotFoundError(name)
        return types.SimpleNamespace(main=modules[short])

    return importer


def dispatch(name, raw, never_blocks=False, **modules):
    """(exit code, parsed stdout or None)"""
    code, out = run.dispatch(name, raw, importer=fake_importer(**modules), never_blocks=never_blocks)
    return code, (json.loads(out) if out else None)


def decision(result):
    return result[1]["hookSpecificOutput"]["permissionDecision"]


def sh_path():
    sh = shutil.which("sh")
    assert sh, "casefile requires sh (Git Bash on Windows)"
    return sh


def test_runs_the_named_hook_with_the_event():
    seen = {}

    def main(event):
        seen.update(event)

    code, out = dispatch("guard_bash", FIXTURE, guard_bash=main)
    assert (code, out) == (0, None)
    assert seen["tool_name"] == "Bash"


def test_a_crashing_guard_denies():
    def main(event):
        raise RuntimeError("boom")

    result = dispatch("guard_bash", FIXTURE, guard_bash=main)
    assert decision(result) == "deny"
    assert "boom" in result[1]["hookSpecificOutput"]["permissionDecisionReason"]


def test_bad_json_denies():
    result = dispatch("guard_bash", "{nope", guard_bash=lambda e: None)
    assert decision(result) == "deny"


def test_unknown_hook_denies():
    assert decision(dispatch("no_such_hook", FIXTURE)) == "deny"


def test_GUARD_007_a_crashing_never_blocks_hook_does_not_block():
    def main(event):
        raise RuntimeError("boom")

    assert dispatch("session_start", "{}", never_blocks=True, session_start=main) == (0, None)


def test_hook_names_are_plain_identifiers():
    assert decision(dispatch("../evil", FIXTURE)) == "deny"


def run_wrapper_without_python(empty, *args, event=FIXTURE):
    """sh runs run-hook with a PATH that holds no Python."""
    env = {k: v for k, v in os.environ.items() if k.upper() != "PATH"}
    env["PATH"] = str(empty)
    return subprocess.run(
        [sh_path(), str(HOOKS / "run-hook"), *args],
        input=event, capture_output=True, text=True, env=env, timeout=30, check=False,
    )


def test_guard_blocks_with_the_install_command(tmp_path):
    proc = run_wrapper_without_python(tmp_path, "guard_bash")
    assert proc.returncode == 2
    assert "Python 3.10" in proc.stderr
    assert "winget install Python.Python.3.14" in proc.stderr


def test_GUARD_007_without_python_session_start_asks_the_developer(tmp_path):
    proc = run_wrapper_without_python(tmp_path, "session_start", "never-blocks", event=SESSION_START)
    assert proc.returncode == 0, proc.stderr
    out = json.loads(proc.stdout)
    context = out["hookSpecificOutput"]["additionalContext"]
    assert out["hookSpecificOutput"]["hookEventName"] == "SessionStart"
    assert "Python 3.10" in context
    assert "wait" in context


def test_GUARD_007_without_python_a_never_blocks_hook_is_silent_on_other_events(tmp_path):
    for name in ("session_start", "stop_lint"):
        proc = run_wrapper_without_python(tmp_path, name, "never-blocks")
        assert (proc.returncode, proc.stdout) == (0, ""), (name, proc.returncode, proc.stderr)


def test_GUARD_007_a_never_blocks_hook_that_cannot_run_prints_nothing():
    for raw in (FIXTURE, "{nope", ""):
        proc = subprocess.run([sys.executable, str(HOOKS / "run.py"), "no_such_hook", "never-blocks"],
                              input=raw, capture_output=True, text=True, timeout=60, check=False)
        assert (proc.returncode, proc.stdout) == (0, ""), (raw, proc.stdout)


def test_GUARD_007_a_session_start_without_never_blocks_is_a_guard():
    assert decision(dispatch("session_start", "{nope", session_start=lambda e: None)) == "deny"


def test_runs_run_py():
    proc = subprocess.run(
        [sh_path(), str(HOOKS / "run-hook"), "no_such_hook"],
        input=FIXTURE, capture_output=True, text=True, timeout=60, check=False,
    )
    assert proc.returncode == 0, proc.stderr
    assert json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"] == "deny"
