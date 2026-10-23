"""hooks/hooks.json registers every hook, each the way it needs to run."""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
MODULES = {p.stem for p in (ROOT / "hooks" / "devflow_hooks").glob("*.py")} - {"__init__", "lib"}
COMMAND = re.compile(r'^sh "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/run-hook" ([a-z_]+)$')
GUARDS = {"guard_bash", "guard_paths", "design_check", "pre_commit"}


def entries():
    """(event, matcher, hook entry, hook name)"""
    for event, groups in HOOKS.items():
        for group in groups:
            for hook in group["hooks"]:
                m = COMMAND.match(hook["command"])
                yield event, group.get("matcher", ""), hook, m.group(1) if m else None


def test_every_command_uses_the_starter():
    for _event, _matcher, hook, name in entries():
        assert name is not None, hook["command"]
        assert "shell" not in hook, "no shell: sh on macOS/Linux, Git Bash on Windows"
        assert "args" not in hook


def test_registered_names_and_modules_match():
    assert {name for *_, name in entries()} == MODULES


def test_guards_fail_closed():
    for _event, _matcher, hook, name in entries():
        if name in GUARDS:
            assert hook.get("onFailure") == "block", name
            assert "timeout" in hook, name
        else:
            assert "onFailure" not in hook, f"{name} only adds context and must never block"


def test_no_if_filters():
    for _event, _matcher, hook, name in entries():
        assert "if" not in hook, f"{name}: the `if` filter is best-effort; the hook checks itself"


def test_what_fires_where():
    where = {(event, name): matcher for event, matcher, _hook, name in entries()}
    assert where[("SessionStart", "session_start")] == "startup|clear|compact"
    for name in ("guard_bash", "pre_commit"):
        assert set(where[("PreToolUse", name)].split("|")) == {"Bash", "PowerShell"}
    for name in ("guard_paths", "design_check"):
        assert set(where[("PreToolUse", name)].split("|")) == {"Edit", "Write", "MultiEdit", "NotebookEdit"}
