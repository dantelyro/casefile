"""hooks/hooks.json registers every hook, each the way it needs to run."""

import json
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
HOOKS = json.loads((ROOT / "hooks" / "hooks.json").read_text(encoding="utf-8"))["hooks"]
MODULES = {p.stem for p in (ROOT / "hooks" / "casefile_hooks").glob("*.py")} - {"__init__", "lib"}
COMMAND = re.compile(r'^sh "\$\{CLAUDE_PLUGIN_ROOT\}/hooks/run-hook" ([a-z_]+)( never-blocks)?$')


def entries():
    """(event, hook entry, hook name, whether it is registered as never-blocks)"""
    for event, groups in HOOKS.items():
        for group in groups:
            for hook in group["hooks"]:
                m = COMMAND.match(hook["command"])
                yield event, hook, m.group(1) if m else None, bool(m and m.group(2))


def test_every_command_uses_the_starter():
    for _event, hook, name, _never_blocks in entries():
        assert name is not None, hook["command"]
        assert "shell" not in hook, "no shell: sh on macOS/Linux, Git Bash on Windows"
        assert "args" not in hook


def test_registered_names_and_modules_match():
    assert {name for _event, _hook, name, _never_blocks in entries()} == MODULES


def test_GUARD_007_a_hook_either_fails_closed_or_never_blocks():
    for event, hook, name, never_blocks in entries():
        if never_blocks:
            assert "onFailure" not in hook, f"{event} {name} only adds context and must never block"
        else:
            assert hook.get("onFailure") == "block", f"{event} {name} is a guard and must fail closed"
            assert "timeout" in hook, name
