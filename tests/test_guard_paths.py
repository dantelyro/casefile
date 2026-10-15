"""guard_paths: which files each kind of session may create or edit."""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run  # noqa: E402

MAIN = None
OTHER_AGENTS = ("Explore", "general-purpose", "other-plugin:helper")
DEVFLOW_AGENTS = ("devflow:reviewer", "devflow:implementer", "devflow:planner")
EVERY_AGENT = OTHER_AGENTS + DEVFLOW_AGENTS


class Base(unittest.TestCase):
    config = {"protected_paths": ["docs/specs/", "docs/product/", "docs/issues/"]}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name) / "repo"
        self.repo.mkdir()
        subprocess.run(["git", "init", "-q"], cwd=self.repo, check=True)
        if self.config is not None:
            (self.repo / ".claude").mkdir()
            (self.repo / ".claude" / "devflow.json").write_text(json.dumps(self.config), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def decide(self, agent, path, tool="Write", cwd=None):
        e = json.loads((FIXTURES / "write_main.json").read_text(encoding="utf-8"))
        e["tool_name"] = tool
        e["cwd"] = str(cwd or self.repo)
        key = "notebook_path" if tool == "NotebookEdit" else "file_path"
        full = path if os.path.isabs(path) else str(self.repo / path)
        e["tool_input"] = {key: full, "content": "x"}
        e.pop("agent_type", None)
        if agent:
            e["agent_type"] = agent
        code, out = run.dispatch("guard_paths", json.dumps(e))
        self.assertEqual(code, 0)
        if not out:
            return "allow", ""
        hso = json.loads(out)["hookSpecificOutput"]
        return hso["permissionDecision"], hso["permissionDecisionReason"]

    def expect(self, agents, paths, decision, **kw):
        for agent in agents:
            for path in paths:
                got, reason = self.decide(agent, path, **kw)
                self.assertEqual(got, decision, f"{agent!r} → {path}: {reason}")


class MainSession(Base):
    def test_unrestricted(self):
        self.expect([MAIN], ("docs/specs/12-matching.md", ".claude/settings.json", "web/a.ts",
                             os.path.join(tempfile.gettempdir(), "x.txt")), "allow")


class ClaudeFolder(Base):
    def test_no_agent_changes_claude_folder(self):
        self.expect(EVERY_AGENT, (".claude/settings.json", ".claude/devflow.json",
                                  ".claude/hooks/x.py", ".claude/agents/reviewer.md"), "deny")

    def test_nor_the_user_claude_folder(self):
        home_claude = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
        self.expect(EVERY_AGENT, (home_claude,), "deny")

    def test_reason_says_what_to_do(self):
        _, reason = self.decide("devflow:implementer", ".claude/settings.json")
        self.assertIn("Report", reason)


class Reviewer(Base):
    def test_writes_nothing(self):
        self.expect(["devflow:reviewer"], ("web/a.ts", "docs/plans/M1.md", "notes.txt"), "deny")
        self.expect(["devflow:reviewer"], ("nb.ipynb",), "deny", tool="NotebookEdit")


class Planner(Base):
    def test_only_its_plan_file(self):
        self.expect(["devflow:planner"], ("docs/plans/M1.md", "docs/plans/saved-jobs.md"), "allow")
        self.expect(["devflow:planner"], ("docs/specs/12-matching.md", "web/a.ts",
                                          "docs/plans/sub/x.md", "docs/plans/M1.txt"), "deny")

    def test_plans_dir_from_config(self):
        (self.repo / ".claude" / "devflow.json").write_text('{"plans_dir": "plans"}', encoding="utf-8")
        self.expect(["devflow:planner"], ("plans/M1.md",), "allow")
        self.expect(["devflow:planner"], ("docs/plans/M1.md",), "deny")


class Implementer(Base):
    def test_writes_code_not_protected_paths(self):
        self.expect(["devflow:implementer"], ("web/features/score.ts", "worker/app/parse.py",
                                              "docs/plans/M1.md", "README.md"), "allow")
        self.expect(["devflow:implementer"], ("docs/specs/12-matching.md", "docs/product/blueprint.html",
                                              "docs/issues/0001-x.md"), "deny")

    def test_reason_says_report_blocked(self):
        _, reason = self.decide("devflow:implementer", "docs/specs/x.md")
        self.assertIn("STATUS: blocked", reason)

    def test_outside_the_repository(self):
        got, reason = self.decide("devflow:implementer", os.path.join(tempfile.gettempdir(), "x.txt"))
        self.assertEqual(got, "deny")
        self.assertIn("outside", reason)

    def test_paths_in_an_agent_worktree_folder_use_their_repo_path(self):
        wt = self.repo / ".claude" / "worktrees" / "agent-1"
        self.expect(["devflow:implementer"], (str(wt / "docs" / "specs" / "x.md"),), "deny")
        self.expect(["devflow:implementer"], (str(wt / "web" / "a.ts"),), "allow")

    def test_inside_a_real_worktree(self):
        subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                        "--allow-empty", "-m", "i"], cwd=self.repo, check=True)
        wt = pathlib.Path(self.tmp.name) / "wt"
        subprocess.run(["git", "worktree", "add", "-q", str(wt)], cwd=self.repo, check=True)
        (wt / ".claude").mkdir(exist_ok=True)
        (wt / ".claude" / "devflow.json").write_text(json.dumps(self.config), encoding="utf-8")
        self.expect(["devflow:implementer"], (str(wt / "docs" / "specs" / "x.md"),), "deny", cwd=wt)
        self.expect(["devflow:implementer"], (str(wt / "web" / "a.ts"),), "allow", cwd=wt)


class OtherAgents(Base):
    def test_only_the_claude_rule_applies(self):
        self.expect(OTHER_AGENTS, ("docs/specs/x.md", "web/a.ts",
                                   os.path.join(tempfile.gettempdir(), "x.txt")), "allow")


class NoConfig(Base):
    config = None

    def test_defaults_protect_nothing_but_claude(self):
        self.expect(["devflow:implementer"], ("docs/specs/x.md",), "allow")
        self.expect(["devflow:implementer"], (".claude/x.json",), "deny")


class BrokenConfig(Base):
    def test_agents_are_refused_main_is_not(self):
        (self.repo / ".claude" / "devflow.json").write_text("{ nope", encoding="utf-8")
        got, reason = self.decide("devflow:implementer", "web/a.ts")
        self.assertEqual(got, "deny")
        self.assertIn(".claude/devflow.json", reason)
        self.expect([MAIN], (".claude/devflow.json",), "allow")


if __name__ == "__main__":
    unittest.main()
