"""session_start: the same context the bash hook gave, in exactly one field."""

import io
import json
import os
import pathlib
import shutil
import subprocess
import sys
import unittest
from contextlib import redirect_stdout
from unittest import mock

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

from devflow_hooks import session_start  # noqa: E402


def expected(name: str) -> dict:
    return json.loads((FIXTURES / "outputs" / f"session_start_{name}.json").read_text(encoding="utf-8"))


def output(env: dict) -> dict:
    out = io.StringIO()
    with mock.patch.dict(os.environ, env, clear=True), redirect_stdout(out):
        session_start.main({"hook_event_name": "SessionStart", "source": "startup"})
    return json.loads(out.getvalue())


class SessionStart(unittest.TestCase):
    def test_under_claude_code_nested_form(self):
        self.assertEqual(output({"CLAUDE_PLUGIN_ROOT": "/x"}), expected("nested"))

    def test_elsewhere_top_level_form(self):
        self.assertEqual(output({}), expected("top"))

    def test_copilot_gets_top_level_form(self):
        self.assertEqual(output({"CLAUDE_PLUGIN_ROOT": "/x", "COPILOT_CLI": "1"}), expected("top"))

    def test_exactly_one_context_field(self):
        for env in ({"CLAUDE_PLUGIN_ROOT": "/x"}, {}):
            out = output(env)
            fields = [k for k in ("additionalContext",) if k in out]
            fields += [k for k in ("additionalContext",) if k in out.get("hookSpecificOutput", {})]
            self.assertEqual(len(fields), 1, out)


@unittest.skipUnless(shutil.which("sh"), "needs sh")
class ThroughTheWrapper(unittest.TestCase):
    def test_wrapper_runs_it(self):
        env = dict(os.environ, CLAUDE_PLUGIN_ROOT=str(HOOKS.parent))
        env.pop("COPILOT_CLI", None)
        proc = subprocess.run([shutil.which("sh"), str(HOOKS / "run-hook"), "session_start"],
                              input=(FIXTURES / "session_start_startup.json").read_text(encoding="utf-8"),
                              capture_output=True, text=True, encoding="utf-8", env=env, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout), expected("nested"))


if __name__ == "__main__":
    unittest.main()
