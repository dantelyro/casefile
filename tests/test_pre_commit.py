"""pre_commit: no skipped tests, no invented styles, and the touched apps' suites pass."""

import json
import os
import pathlib
import shutil
import subprocess
import sys

import pytest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "plugins" / "devflow" / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run

# Sample input for the check under test, kept out of literal test code so this file itself
# carries no markers.
SKIP = "it." + "skip"
ONLY = "test." + "only"
XFAIL = "@pytest.mark." + "xfail"


def git(repo, *args):
    subprocess.run(["git", *args], cwd=repo, check=True, timeout=60)


class Repo:
    """A temporary git repository, and the pre_commit hook run against it."""

    def __init__(self, path, monkeypatch, config):
        self.path = path
        self.monkeypatch = monkeypatch
        for args in (["init", "-q"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            git(path, *args)
        self.write("README.md", "x")
        if config is not None:
            self.write(".claude/devflow.json", json.dumps(config))
        git(path, "add", "-A")
        git(path, "commit", "-qm", "init")

    def write(self, rel, text):
        path = self.path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def commit_all(self, message="t"):
        git(self.path, "add", "-A")
        git(self.path, "commit", "-qm", message, "--no-verify")

    def check(self, command="git commit -m test", stage=True, agent=None, path=None, cwd=None):
        if stage:
            git(self.path, "add", "-A")
        e = json.loads((FIXTURES / "bash_main.json").read_text(encoding="utf-8"))
        e.update({"cwd": str(cwd or self.path), "tool_input": {"command": command}})
        e.pop("agent_type", None)
        if agent:
            e["agent_type"] = agent
        with self.monkeypatch.context() as m:  # PATH is changed for this call only
            if path is not None:
                m.setenv("PATH", path)
            code, out = run.dispatch("pre_commit", json.dumps(e))
        assert code == 0
        if not out:
            return "allow", ""
        hso = json.loads(out)["hookSpecificOutput"]
        return hso["permissionDecision"], hso["permissionDecisionReason"]

    def expect(self, decision, **kw):
        got, reason = self.check(**kw)
        assert got == decision, reason
        return reason


@pytest.fixture
def make_repo(tmp_path, monkeypatch):
    """A factory: make_repo(config) builds the repository with that .claude/devflow.json."""

    def make(config=None):
        return Repo(tmp_path / "repo", monkeypatch, config)

    (tmp_path / "repo").mkdir()
    return make


@pytest.fixture
def repo(make_repo):
    return make_repo({})


@pytest.fixture
def stub_dir(tmp_path_factory):
    """A factory: stub_dir(tool, exit_code) is a folder holding a fake tool that prints and exits."""

    def make(tool: str, exit_code: int) -> str:
        d = tmp_path_factory.mktemp("stub")
        if os.name == "nt":
            (d / (tool + ".cmd")).write_text(f"@echo STUB {tool} ran\n@exit /b {exit_code}\n")
        else:
            p = d / tool
            p.write_text(f"#!/bin/sh\necho STUB {tool} ran\nexit {exit_code}\n")
            p.chmod(0o755)
        return str(d)

    return make


def with_real_path(*dirs):
    return os.pathsep.join([*dirs, os.environ["PATH"]])


def test_only_a_commit_statement_triggers_it(repo):
    repo.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
    repo.expect("allow", command="git status")
    repo.expect("allow", command='echo "git commit"')
    repo.expect("deny", command="cd web && git commit -m x")
    repo.expect("deny", command="git -C . commit -m x")


def test_git_dash_c_checks_that_repository(repo, tmp_path):
    repo.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
    git(repo.path, "add", "-A")
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    repo.expect("deny", stage=False, cwd=elsewhere, command=f'git -C "{repo.path}" commit -m x')


def test_nothing_staged(repo):
    repo.expect("allow", stage=False)


def test_commit_all_checks_unstaged_tracked_changes(repo):
    repo.write("web/a.test.ts", "it('x', () => {})\n")
    git(repo.path, "add", "-A")
    git(repo.path, "commit", "-qm", "t")
    repo.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
    repo.expect("allow", stage=False)  # nothing staged: plain commit commits nothing
    repo.expect("deny", stage=False, command="git commit -am x")
    repo.expect("deny", stage=False, command="git commit --all -m x")


def test_docs_only_commit_passes(repo):
    repo.write("docs/specs/x.md", "# rule")
    repo.expect("allow")


@pytest.mark.parametrize(
    ("path", "line"),
    [
        ("web/features/score.test.ts", f"{SKIP}('MATCH-010: x', () => {{}})"),
        ("web/e2e/upload.spec.ts", f"{ONLY}('CV-001', async () => {{}})"),
        ("worker/tests/test_skills.py", f"{XFAIL}\ndef test_MATCH_002(): pass"),
        ("tests/test_x.py", "@unittest." + "skip('later')"),
    ],
)
def test_skipped_and_focused_tests_are_refused(repo, path, line):
    repo.write(path, line + "\n")
    reason = repo.expect("deny")
    assert path in reason


def test_skip_word_in_normal_code_is_fine(repo):
    repo.write("web/features/jobs/list.ts", "const skip = 20; items.skip(1)\n")
    repo.expect("allow")


def test_removed_lines_do_not_count(repo):
    repo.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
    repo.commit_all()
    repo.write("web/a.test.ts", "it('x', () => {})\n")
    repo.expect("allow")


def test_configured_files_may_hold_markers_as_sample_data(make_repo):
    repo = make_repo({"allow_skip_markers_in": ["tests/test_pre_commit.py", "hooks/tests/"]})
    repo.write("tests/test_pre_commit.py", f'SAMPLE = "{SKIP}(x)"\n')
    repo.write("hooks/tests/test_y.py", f'SAMPLE = "{SKIP}(x)"\n')
    repo.expect("allow")
    repo.write("tests/test_other.py", f'SAMPLE = "{SKIP}(x)"\n')
    repo.expect("deny")


@pytest.fixture
def design_repo(make_repo):
    repo = make_repo({"design": {"ui_paths": ["web/"], "classes": "tailwind"}})
    shutil.copytree(FIXTURES / "design", repo.path / "docs" / "product" / "design-system")
    return repo


def test_invented_styles_written_outside_the_edit_tools_are_refused(design_repo):
    design_repo.write("web/app/page.tsx", '<main className="bg-blue-500 p-5" />\n')
    reason = design_repo.expect("deny")
    assert "design system" in reason


def test_only_added_lines_are_checked(design_repo):
    design_repo.write("web/app/page.tsx", '<main className="bg-blue-500" />\n')
    design_repo.commit_all("old")
    design_repo.write("web/app/page.tsx", '<main className="bg-blue-500" />\n<p className="text-ink" />\n')
    design_repo.expect("allow")


@pytest.fixture
def apps_repo(make_repo):
    return make_repo({"apps": {"web": {"test": "npm test"}, "worker": {"test": "uv run pytest -q"}}})


def test_passing_suite_allows(apps_repo, stub_dir):
    apps_repo.write("web/package.json", "{}")
    apps_repo.expect("allow", path=with_real_path(stub_dir("npm", 0)))


def test_failing_suite_refuses_with_its_output(apps_repo, stub_dir):
    apps_repo.write("web/package.json", "{}")
    reason = apps_repo.expect("deny", path=with_real_path(stub_dir("npm", 1)))
    assert "web" in reason
    assert "STUB npm ran" in reason


def test_untouched_app_is_not_run(apps_repo, stub_dir):
    apps_repo.write("web/package.json", "{}")
    apps_repo.commit_all("web")
    apps_repo.write("docs/x.md", "x")
    apps_repo.expect("allow", path=with_real_path(stub_dir("npm", 1)))


def test_each_touched_app_runs(apps_repo, stub_dir):
    apps_repo.write("web/package.json", "{}")
    apps_repo.write("worker/app.py", "x")
    reason = apps_repo.expect("deny", path=with_real_path(stub_dir("npm", 0), stub_dir("uv", 1)))
    assert "worker" in reason


@pytest.fixture
def lint_repo(make_repo):
    return make_repo({"apps": {"web": {"test": "npm test", "lint": "eslint ."}}})


def test_failing_lint_refuses_after_passing_tests(lint_repo, stub_dir):
    lint_repo.write("web/a.ts", "x")
    reason = lint_repo.expect("deny", path=with_real_path(stub_dir("npm", 0), stub_dir("eslint", 1)))
    assert "web lint fails" in reason
    assert "STUB eslint ran" in reason


def test_passing_lint_allows(lint_repo, stub_dir):
    lint_repo.write("web/a.ts", "x")
    lint_repo.expect("allow", path=with_real_path(stub_dir("npm", 0), stub_dir("eslint", 0)))


def test_missing_tool_says_so_instead_of_failing_tests(make_repo):
    # A tool name that exists nowhere. Trimming PATH to hide npm does not work everywhere: on
    # macOS runners git and npm share a folder.
    repo = make_repo({"apps": {"web": {"test": "devflow-no-such-tool run"}}})
    repo.write("web/package.json", "{}")
    reason = repo.expect("deny")
    assert "devflow-no-such-tool" in reason
    assert "did not run" in reason


def test_runs_when_its_path_is_touched(make_repo, stub_dir):
    repo = make_repo({"apps": {"frontend": {"path": "apps/web", "test": "npm test"}}})
    repo.write("apps/web/x.ts", "x")
    repo.expect("deny", path=with_real_path(stub_dir("npm", 1)))


@pytest.fixture
def whole_repo_app(make_repo):
    return make_repo({"apps": {"app": {"path": ".", "test": "npm test"}}})


def test_any_file_runs_it(whole_repo_app, stub_dir):
    whole_repo_app.write("src/index.ts", "x")
    reason = whole_repo_app.expect("deny", path=with_real_path(stub_dir("npm", 1)))
    assert "STUB npm ran" in reason


def test_it_passes_too(whole_repo_app, stub_dir):
    whole_repo_app.write("README.md", "changed")
    whole_repo_app.expect("allow", path=with_real_path(stub_dir("npm", 0)))


@pytest.mark.parametrize("name", ["a.test.mts", "a.spec.cts", "a.test.mjs", "a.spec.cjs"])
def test_module_extensions_are_test_files_too(repo, name):
    repo.write(f"src/{name}", f"{SKIP}('x', () => {{}})\n")
    repo.expect("deny")


def test_no_suites_run(make_repo, stub_dir):
    repo = make_repo(None)
    repo.write("web/x.ts", "x")
    repo.expect("allow", path=with_real_path(stub_dir("npm", 1)))


def test_agents_too(repo):
    repo.write("web/a.test.ts", f"{SKIP}('x', () => {{}})\n")
    repo.expect("deny", agent="devflow:implementer")
    repo.expect("deny", agent="general-purpose")
