"""The shared hook library: reading events, decisions, who is acting, paths, config."""

import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "hooks"))

from devflow_hooks import lib  # noqa: E402

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def decision_of(fn, *args) -> dict:
    """Run a decision function, check it exits 0, and return the JSON it printed."""
    out = io.StringIO()
    with redirect_stdout(out), self_exit() as code:
        fn(*args)
    assert code == [0], code
    return json.loads(out.getvalue())


class self_exit:
    """Context manager that catches SystemExit and records its code."""

    def __enter__(self):
        self.codes = []
        return self.codes

    def __exit__(self, kind, value, tb):
        if kind is SystemExit:
            self.codes.append(value.code or 0)
            return True
        return False


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


class ReadEvent(unittest.TestCase):
    def test_every_fixture_parses(self):
        for path in FIXTURES.glob("*.json"):
            raw = path.read_bytes()
            with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8")):
                event = lib.read_event()
            self.assertIn("hook_event_name", event, path.name)

    def test_bad_json_raises(self):
        with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"{not json"), encoding="utf-8")):
            with self.assertRaises(ValueError):
                lib.read_event()

    def test_empty_input_raises(self):
        with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(b""), encoding="utf-8")):
            with self.assertRaises(ValueError):
                lib.read_event()

    def test_non_ascii_path_survives(self):
        raw = json.dumps({"hook_event_name": "PreToolUse", "cwd": "C:\\Usuários\\joão"}, ensure_ascii=False)
        with mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(raw.encode("utf-8")), encoding="utf-8")):
            self.assertEqual(lib.read_event()["cwd"], "C:\\Usuários\\joão")


class Decisions(unittest.TestCase):
    def test_deny(self):
        out = decision_of(lib.deny, "no pushing from agents")
        self.assertEqual(out, {"hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "permissionDecision": "deny",
            "permissionDecisionReason": "devflow: no pushing from agents",
        }})

    def test_ask(self):
        out = decision_of(lib.ask, "push to the remote?")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertEqual(out["hookSpecificOutput"]["permissionDecisionReason"], "devflow: push to the remote?")

    def test_allow_prints_nothing(self):
        out = io.StringIO()
        with redirect_stdout(out), self_exit() as code:
            lib.allow()
        self.assertEqual((out.getvalue(), code), ("", [0]))


class AgentOf(unittest.TestCase):
    def test_main_session_is_none(self):
        self.assertIsNone(lib.agent_of(fixture("bash_main")))
        self.assertIsNone(lib.agent_of(fixture("bash_main_auto")))
        self.assertIsNone(lib.agent_of(fixture("powershell_main")))

    def test_plugin_agent(self):
        self.assertEqual(lib.agent_of(fixture("bash_plugin_agent")), "devflow:reviewer")

    def test_builtin_agent(self):
        self.assertEqual(lib.agent_of(fixture("bash_builtin_agent")), "Explore")

    def test_devflow_agent_name(self):
        self.assertEqual(lib.devflow_agent(fixture("bash_plugin_agent")), "reviewer")
        self.assertIsNone(lib.devflow_agent(fixture("bash_builtin_agent")))
        self.assertIsNone(lib.devflow_agent(fixture("bash_main")))


class Paths(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        git("init", "-q", cwd=self.repo)
        git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init",
            cwd=self.repo)

    def tearDown(self):
        self.tmp.cleanup()

    def same(self, a, b):
        self.assertEqual(os.path.normcase(os.path.realpath(a)), os.path.normcase(os.path.realpath(b)))

    def test_git_root(self):
        (self.repo / "web").mkdir()
        self.same(lib.git_root(str(self.repo / "web")), self.repo)

    def test_git_root_outside_a_repo(self):
        self.assertIsNone(lib.git_root(self.tmp.name))

    def test_relative_and_absolute_paths(self):
        event = {"cwd": str(self.repo)}
        self.assertEqual(lib.repo_relative(event, "web/a.ts"), "web/a.ts")
        self.assertEqual(lib.repo_relative(event, str(self.repo / "web" / "a.ts")), "web/a.ts")

    def test_path_into_an_agent_worktree_folder(self):
        event = {"cwd": str(self.repo)}
        path = self.repo / ".claude" / "worktrees" / "agent-1" / "web" / "a.ts"
        self.assertEqual(lib.repo_relative(event, str(path)), "web/a.ts")

    def test_inside_a_real_worktree(self):
        wt = pathlib.Path(self.tmp.name) / "wt"
        git("worktree", "add", "-q", str(wt), cwd=self.repo)
        event = {"cwd": str(wt)}
        self.assertEqual(lib.repo_relative(event, str(wt / "docs" / "x.md")), "docs/x.md")

    def test_outside_the_repo(self):
        event = {"cwd": str(self.repo)}
        self.assertIsNone(lib.repo_relative(event, str(pathlib.Path(self.tmp.name) / "elsewhere.txt")))

    def test_no_path(self):
        self.assertIsNone(lib.repo_relative({"cwd": str(self.repo)}, None))


class Config(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        git("init", "-q", cwd=self.repo)
        self.event = {"cwd": str(self.repo)}

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, text: str):
        (self.repo / ".claude").mkdir(exist_ok=True)
        (self.repo / ".claude" / "devflow.json").write_text(text, encoding="utf-8")

    def test_no_file_gives_defaults(self):
        cfg = lib.config(self.event)
        self.assertEqual(cfg["default_branch"], "main")
        self.assertEqual(cfg["protected_paths"], [])
        self.assertEqual(cfg["apps"], {})
        self.assertEqual(cfg["design"]["tokens"], "docs/product/design-system/tokens.json")
        self.assertEqual(cfg["design"]["ui_paths"], [])
        self.assertEqual(cfg["build_order"], "docs/product/blueprint.html")

    def test_partial_file_keeps_other_defaults(self):
        self.write('{"protected_paths": ["docs/specs/"], "design": {"ui_paths": ["web/"]}}')
        cfg = lib.config(self.event)
        self.assertEqual(cfg["protected_paths"], ["docs/specs/"])
        self.assertEqual(cfg["default_branch"], "main")
        self.assertEqual(cfg["design"]["ui_paths"], ["web/"])
        self.assertEqual(cfg["design"]["tokens"], "docs/product/design-system/tokens.json")

    def test_invalid_json_names_the_file(self):
        self.write("{ nope")
        with self.assertRaises(lib.ConfigError) as caught:
            lib.config(self.event)
        self.assertIn(".claude/devflow.json", str(caught.exception))

    def test_wrong_type_names_the_key(self):
        self.write('{"protected_paths": "docs/"}')
        with self.assertRaises(lib.ConfigError) as caught:
            lib.config(self.event)
        self.assertIn("protected_paths", str(caught.exception))

    def test_outside_a_repo_gives_defaults(self):
        with tempfile.TemporaryDirectory() as plain:
            self.assertEqual(lib.config({"cwd": plain})["apps"], {})


if __name__ == "__main__":
    unittest.main()
