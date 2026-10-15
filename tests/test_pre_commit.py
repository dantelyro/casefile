"""pre_commit: no skipped tests, no invented styles, and the touched apps' suites pass."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run  # noqa: E402

# Sample input for the check under test, kept out of literal test code so this file itself
# carries no markers.
SKIP = "it." + "skip"
ONLY = "test." + "only"
XFAIL = "@pytest.mark." + "xfail"


class Base(unittest.TestCase):
    config: dict | None = {}

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.repo, check=True)
        self.write("README.md", "x")
        if self.config is not None:
            self.write(".claude/devflow.json", json.dumps(self.config))
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "init"], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        path = self.repo / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def check(self, command="git commit -m test", stage=True, agent=None, path=None):
        if stage:
            subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        e = json.loads((FIXTURES / "bash_main.json").read_text(encoding="utf-8"))
        e.update({"cwd": str(self.repo), "tool_input": {"command": command}})
        e.pop("agent_type", None)
        if agent:
            e["agent_type"] = agent
        env = {"PATH": path} if path is not None else {}
        with mock.patch.dict(os.environ, env):
            code, out = run.dispatch("pre_commit", json.dumps(e))
        self.assertEqual(code, 0)
        if not out:
            return "allow", ""
        hso = json.loads(out)["hookSpecificOutput"]
        return hso["permissionDecision"], hso["permissionDecisionReason"]

    def expect(self, decision, **kw):
        got, reason = self.check(**kw)
        self.assertEqual(got, decision, reason)
        return reason


class Trigger(Base):
    def test_only_a_commit_statement_triggers_it(self):
        self.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
        self.expect("allow", command="git status")
        self.expect("allow", command='echo "git commit"')
        self.expect("deny", command="cd web && git commit -m x")
        self.expect("deny", command="git -C . commit -m x")

    def test_git_dash_c_checks_that_repository(self):
        self.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        with tempfile.TemporaryDirectory() as elsewhere:
            e = json.loads((FIXTURES / "bash_main.json").read_text(encoding="utf-8"))
            e.update({"cwd": elsewhere, "tool_input": {"command": f'git -C "{self.repo}" commit -m x'}})
            code, out = run.dispatch("pre_commit", json.dumps(e))
        self.assertEqual(json.loads(out)["hookSpecificOutput"]["permissionDecision"], "deny")

    def test_nothing_staged(self):
        self.expect("allow", stage=False)

    def test_commit_all_checks_unstaged_tracked_changes(self):
        self.write("web/a.test.ts", "it('x', () => {})\n")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "t"], cwd=self.repo, check=True)
        self.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
        self.expect("allow", stage=False)  # nothing staged: plain commit commits nothing
        self.expect("deny", stage=False, command="git commit -am x")
        self.expect("deny", stage=False, command="git commit --all -m x")


class SkippedTests(Base):
    def test_docs_only_commit_passes(self):
        self.write("docs/specs/x.md", "# rule")
        self.expect("allow")

    def test_skipped_and_focused_tests_are_refused(self):
        for path, line in (("web/features/score.test.ts", f"{SKIP}('MATCH-010: x', () => {{}})"),
                           ("web/e2e/upload.spec.ts", f"{ONLY}('CV-001', async () => {{}})"),
                           ("worker/tests/test_skills.py", f"{XFAIL}\ndef test_MATCH_002(): pass"),
                           ("tests/test_x.py", "@unittest." + "skip('later')")):
            with self.subTest(path=path):
                self.write(path, line + "\n")
                reason = self.expect("deny")
                self.assertIn(path, reason)
                subprocess.run(["git", "reset", "-q", "--hard"], cwd=self.repo, check=True)
                subprocess.run(["git", "clean", "-qfd"], cwd=self.repo, check=True)

    def test_skip_word_in_normal_code_is_fine(self):
        self.write("web/features/jobs/list.ts", "const skip = 20; items.skip(1)\n")
        self.expect("allow")

    def test_removed_lines_do_not_count(self):
        self.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "t", "--no-verify"], cwd=self.repo, check=True)
        self.write("web/a.test.ts", "it('x', () => {})\n")
        self.expect("allow")


class SkipMarkersAllowedIn(Base):
    config = {"allow_skip_markers_in": ["tests/test_pre_commit.py", "hooks/tests/"]}

    def test_configured_files_may_hold_markers_as_sample_data(self):
        self.write("tests/test_pre_commit.py", f'SAMPLE = "{SKIP}(x)"\n')
        self.write("hooks/tests/test_y.py", f'SAMPLE = "{SKIP}(x)"\n')
        self.expect("allow")
        self.write("tests/test_other.py", f'SAMPLE = "{SKIP}(x)"\n')
        self.expect("deny")


class Design(Base):
    config = {"design": {"ui_paths": ["web/"], "classes": "tailwind"}}

    def setUp(self):
        super().setUp()
        shutil.copytree(FIXTURES / "design", self.repo / "docs" / "product" / "design-system")

    def test_invented_styles_written_outside_the_edit_tools_are_refused(self):
        self.write("web/app/page.tsx", '<main className="bg-blue-500 p-5" />\n')
        reason = self.expect("deny")
        self.assertIn("design system", reason)

    def test_only_added_lines_are_checked(self):
        self.write("web/app/page.tsx", '<main className="bg-blue-500" />\n')
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "old", "--no-verify"], cwd=self.repo, check=True)
        self.write("web/app/page.tsx", '<main className="bg-blue-500" />\n<p className="text-ink" />\n')
        self.expect("allow")


def stub_dir(tool: str, exit_code: int) -> str:
    """A folder holding a fake `tool` that prints a line and exits with `exit_code`."""
    d = tempfile.mkdtemp(prefix="stub-")
    if os.name == "nt":
        pathlib.Path(d, tool + ".cmd").write_text(f"@echo STUB {tool} ran\n@exit /b {exit_code}\n")
    else:
        p = pathlib.Path(d, tool)
        p.write_text(f"#!/bin/sh\necho STUB {tool} ran\nexit {exit_code}\n")
        p.chmod(0o755)
    return d


class Apps(Base):
    config = {"apps": {"web": {"test": "npm test"}, "worker": {"test": "uv run pytest -q"}}}

    def path_with(self, tool, code):
        return stub_dir(tool, code) + os.pathsep + os.environ["PATH"]

    def test_passing_suite_allows(self):
        self.write("web/package.json", "{}")
        self.expect("allow", path=self.path_with("npm", 0))

    def test_failing_suite_refuses_with_its_output(self):
        self.write("web/package.json", "{}")
        reason = self.expect("deny", path=self.path_with("npm", 1))
        self.assertIn("web", reason)
        self.assertIn("STUB npm ran", reason)

    def test_untouched_app_is_not_run(self):
        self.write("web/package.json", "{}")
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        subprocess.run(["git", "commit", "-qm", "web", "--no-verify"], cwd=self.repo, check=True)
        self.write("docs/x.md", "x")
        self.expect("allow", path=self.path_with("npm", 1))

    def test_each_touched_app_runs(self):
        self.write("web/package.json", "{}")
        self.write("worker/app.py", "x")
        reason = self.expect("deny", path=self.path_with("npm", 0) + os.pathsep + stub_dir("uv", 1))
        self.assertIn("worker", reason)

    def test_missing_tool_says_so_instead_of_failing_tests(self):
        self.write("web/package.json", "{}")
        git_dir = os.path.dirname(shutil.which("git"))
        system = [os.path.join(os.environ.get("SystemRoot", ""), "System32")] if os.name == "nt" else []
        reason = self.expect("deny", path=os.pathsep.join([git_dir, *system]))
        self.assertIn("npm", reason)
        self.assertIn("did not run", reason)


class AppPathFromConfig(Base):
    config = {"apps": {"frontend": {"path": "apps/web", "test": "npm test"}}}

    def test_runs_when_its_path_is_touched(self):
        self.write("apps/web/x.ts", "x")
        self.expect("deny", path=stub_dir("npm", 1) + os.pathsep + os.environ["PATH"])


class WholeRepositoryApp(Base):
    config = {"apps": {"app": {"path": ".", "test": "npm test"}}}

    def test_any_file_runs_it(self):
        self.write("src/index.ts", "x")
        reason = self.expect("deny", path=stub_dir("npm", 1) + os.pathsep + os.environ["PATH"])
        self.assertIn("STUB npm ran", reason)

    def test_it_passes_too(self):
        self.write("README.md", "changed")
        self.expect("allow", path=stub_dir("npm", 0) + os.pathsep + os.environ["PATH"])


class NodeTestFileNames(Base):
    def test_module_extensions_are_test_files_too(self):
        for name in ("a.test.mts", "a.spec.cts", "a.test.mjs", "a.spec.cjs"):
            with self.subTest(name=name):
                self.write(f"src/{name}", f"{SKIP}('x', () => {{}})\n")
                self.expect("deny")
                subprocess.run(["git", "reset", "-q", "--hard"], cwd=self.repo, check=True)
                subprocess.run(["git", "clean", "-qfd"], cwd=self.repo, check=True)


class NoApps(Base):
    config = None

    def test_no_suites_run(self):
        self.write("web/x.ts", "x")
        self.expect("allow", path=stub_dir("npm", 1) + os.pathsep + os.environ["PATH"])


class Everyone(Base):
    def test_agents_too(self):
        self.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
        self.expect("deny", agent="devflow:implementer")
        self.expect("deny", agent="general-purpose")


if __name__ == "__main__":
    unittest.main()
