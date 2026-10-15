"""hooks/hooks.json registers every hook, each the way it needs to run."""

import json
import pathlib
import re
import unittest

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


class Registration(unittest.TestCase):
    def test_every_command_uses_the_starter(self):
        for event, matcher, hook, name in entries():
            self.assertIsNotNone(name, hook["command"])
            self.assertNotIn("shell", hook, "no shell: sh on macOS/Linux, Git Bash on Windows")
            self.assertNotIn("args", hook)

    def test_registered_names_and_modules_match(self):
        self.assertEqual({name for *_, name in entries()}, MODULES)

    def test_guards_fail_closed(self):
        for event, matcher, hook, name in entries():
            if name in GUARDS:
                self.assertEqual(hook.get("onFailure"), "block", name)
                self.assertIn("timeout", hook, name)
            else:
                self.assertNotIn("onFailure", hook, f"{name} only adds context and must never block")

    def test_no_if_filters(self):
        for event, matcher, hook, name in entries():
            self.assertNotIn("if", hook, f"{name}: the `if` filter is best-effort; the hook checks itself")

    def test_what_fires_where(self):
        where = {(event, name): matcher for event, matcher, hook, name in entries()}
        self.assertEqual(where[("SessionStart", "session_start")], "startup|clear|compact")
        for name in ("guard_bash", "pre_commit"):
            self.assertEqual(set(where[("PreToolUse", name)].split("|")), {"Bash", "PowerShell"})
        for name in ("guard_paths", "design_check"):
            self.assertEqual(set(where[("PreToolUse", name)].split("|")),
                             {"Edit", "Write", "MultiEdit", "NotebookEdit"})


if __name__ == "__main__":
    unittest.main()
