"""The launcher (run.py) and the starter (run-hook): guards fail closed."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import types
import unittest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
sys.path.insert(0, str(HOOKS))

import run  # noqa: E402

FIXTURE = (pathlib.Path(__file__).resolve().parent / "fixtures" / "bash_main.json").read_text(encoding="utf-8")


def fake_importer(**modules):
    def importer(name):
        short = name.rsplit(".", 1)[-1]
        if short not in modules:
            raise ModuleNotFoundError(name)
        return types.SimpleNamespace(main=modules[short])
    return importer


class Launcher(unittest.TestCase):
    def dispatch(self, name, raw, **modules):
        """(exit code, parsed stdout or None)"""
        code, out = run.dispatch(name, raw, importer=fake_importer(**modules))
        return code, (json.loads(out) if out else None)

    def decision(self, result):
        return result[1]["hookSpecificOutput"]["permissionDecision"]

    def test_runs_the_named_hook_with_the_event(self):
        seen = {}

        def main(event):
            seen.update(event)
        code, out = self.dispatch("guard_bash", FIXTURE, guard_bash=main)
        self.assertEqual((code, out), (0, None))
        self.assertEqual(seen["tool_name"], "Bash")

    def test_a_crashing_guard_denies(self):
        def main(event):
            raise RuntimeError("boom")
        result = self.dispatch("guard_bash", FIXTURE, guard_bash=main)
        self.assertEqual(self.decision(result), "deny")
        self.assertIn("boom", result[1]["hookSpecificOutput"]["permissionDecisionReason"])

    def test_bad_json_denies(self):
        result = self.dispatch("guard_bash", "{nope", guard_bash=lambda e: None)
        self.assertEqual(self.decision(result), "deny")

    def test_unknown_hook_denies(self):
        result = self.dispatch("no_such_hook", FIXTURE)
        self.assertEqual(self.decision(result), "deny")

    def test_a_crashing_session_start_never_blocks(self):
        def main(event):
            raise RuntimeError("boom")
        self.assertEqual(self.dispatch("session_start", "{}", session_start=main), (0, None))

    def test_hook_names_are_plain_identifiers(self):
        result = self.dispatch("../evil", FIXTURE)
        self.assertEqual(self.decision(result), "deny")


@unittest.skipUnless(shutil.which("sh"), "needs sh")
class WrapperWithoutPython(unittest.TestCase):
    """sh runs run-hook with a PATH that holds no Python."""

    def run_wrapper(self, name):
        with tempfile.TemporaryDirectory() as empty:
            env = {k: v for k, v in os.environ.items() if k.upper() != "PATH"}
            env["PATH"] = empty
            return subprocess.run([shutil.which("sh"), str(HOOKS / "run-hook"), name],
                                  input=FIXTURE, capture_output=True, text=True, env=env, timeout=30)

    def test_guard_blocks_with_the_install_command(self):
        proc = self.run_wrapper("guard_bash")
        self.assertEqual(proc.returncode, 2)
        self.assertIn("Python 3.10", proc.stderr)
        self.assertIn("winget install Python.Python.3.14", proc.stderr)

    def test_session_start_asks_the_developer(self):
        proc = self.run_wrapper("session_start")
        self.assertEqual(proc.returncode, 0, proc.stderr)
        out = json.loads(proc.stdout)
        context = out["hookSpecificOutput"]["additionalContext"]
        self.assertEqual(out["hookSpecificOutput"]["hookEventName"], "SessionStart")
        self.assertIn("Python 3.10", context)
        self.assertIn("wait", context)


@unittest.skipUnless(shutil.which("sh"), "needs sh")
class WrapperWithPython(unittest.TestCase):
    def test_runs_run_py(self):
        proc = subprocess.run([shutil.which("sh"), str(HOOKS / "run-hook"), "no_such_hook"],
                              input=FIXTURE, capture_output=True, text=True, timeout=60)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["hookSpecificOutput"]["permissionDecision"], "deny")


if __name__ == "__main__":
    unittest.main()
