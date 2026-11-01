"""guard_paths: which files each kind of session may create or edit."""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
from unittest import mock

import pytest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run
from casefile_hooks import lib
from casefile_hooks.pre_commit import TEST_FILE

MAIN = None
OTHER_AGENTS = ("Explore", "general-purpose", "other-plugin:helper")
CASEFILE_AGENTS = ("casefile:reviewer", "casefile:implementer", "casefile:planner")
EVERY_AGENT = OTHER_AGENTS + CASEFILE_AGENTS

CONFIG = {"protected_paths": ["docs/specs/", "docs/product/", "docs/issues/"]}


def make_repo(root, config):
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    if config is not None:
        (root / ".claude").mkdir()
        (root / ".claude" / "casefile.json").write_text(json.dumps(config), encoding="utf-8")
    return root


def commit_empty(repo):
    subprocess.run(["git", "-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q",
                    "--allow-empty", "-m", "i"], cwd=repo, check=True)


def add_worktree(repo, path):
    subprocess.run(["git", "worktree", "add", "-q", str(path)], cwd=repo, check=True)
    return path


@pytest.fixture
def repo(tmp_path):
    return make_repo(tmp_path / "repo", CONFIG)


@pytest.fixture
def bare_repo(tmp_path):
    """A repository with no `.claude/casefile.json`."""
    return make_repo(tmp_path / "repo", None)


@pytest.fixture
def wt(repo):
    """A real linked worktree of `repo`, where a reviewer's session runs."""
    commit_empty(repo)
    return add_worktree(repo, repo / ".claude" / "worktrees" / "agent-1")


def decide(repo, agent, path, tool="Write", cwd=None, raw_path=False):
    e = json.loads((FIXTURES / "write_main.json").read_text(encoding="utf-8"))
    e["tool_name"] = tool
    e["cwd"] = str(cwd or repo)
    key = "notebook_path" if tool == "NotebookEdit" else "file_path"
    full = path if raw_path or os.path.isabs(path) else str(repo / path)
    e["tool_input"] = {key: full, "content": "x"}
    e.pop("agent_type", None)
    if agent:
        e["agent_type"] = agent
    code, out = run.dispatch("guard_paths", json.dumps(e))
    assert code == 0
    if not out:
        return "allow", ""
    hso = json.loads(out)["hookSpecificOutput"]
    return hso["permissionDecision"], hso["permissionDecisionReason"]


def expect(repo, agents, paths, decision, **kw):
    for agent in agents:
        for path in paths:
            got, reason = decide(repo, agent, path, **kw)
            assert got == decision, f"{agent!r} → {path}: {reason}"


class TestMainSession:
    def test_unrestricted(self, repo):
        expect(repo, [MAIN], ("docs/specs/12-matching.md", ".claude/settings.json", "web/a.ts",
                              os.path.join(tempfile.gettempdir(), "x.txt")), "allow")


class TestClaudeFolder:
    def test_no_agent_changes_claude_folder(self, repo):
        expect(repo, EVERY_AGENT, (".claude/settings.json", ".claude/casefile.json",
                                   ".claude/hooks/x.py", ".claude/agents/reviewer.md"), "deny")

    def test_nor_the_user_claude_folder(self, repo):
        home_claude = os.path.join(os.path.expanduser("~"), ".claude", "settings.json")
        expect(repo, EVERY_AGENT, (home_claude,), "deny")

    def test_reason_says_what_to_do(self, repo):
        _, reason = decide(repo, "casefile:implementer", ".claude/settings.json")
        assert "Report" in reason


class TestReviewer:
    def test_GUARD_002_writes_no_records_in_the_checkout(self, repo):
        expect(repo, ["casefile:reviewer"], ("docs/plans/M1.md", "docs/issues/0001-x.md"), "deny")


EDITS = (("Edit", "web/a.ts"), ("Write", "web/a.ts"), ("MultiEdit", "web/a.ts"),
         ("NotebookEdit", "nb.ipynb"), ("Write", "web/new-folder/b.ts"))


class TestReviewerCheckout:
    """GUARD-001: the reviewer breaks code in the developer's checkout, with no worktree (D-072)."""

    @pytest.mark.parametrize(("tool", "path"), EDITS)
    def test_GUARD_001_reviewer_may_edit_product_code_in_the_checkout(self, tool, path, repo):
        got, reason = decide(repo, "casefile:reviewer", path, tool=tool)
        assert got == "allow", f"{tool} {path}: {reason}"

    def test_GUARD_001_a_relative_path_resolves_against_the_cwd(self, repo):
        (repo / "web").mkdir()
        got, reason = decide(repo, "casefile:reviewer", "a.ts", cwd=repo / "web", raw_path=True)
        assert got == "allow", reason

    def test_GUARD_001_reviewer_is_denied_outside_any_repository(self, repo, tmp_path):
        other = tmp_path / "elsewhere"
        other.mkdir()
        got, _ = decide(repo, "casefile:reviewer", str(other / "x.txt"), cwd=other)
        assert got == "deny"

    def test_GUARD_001_reviewer_is_denied_in_another_repository(self, repo, tmp_path):
        other = make_repo(tmp_path / "other", None)
        got, reason = decide(repo, "casefile:reviewer", str(other / "web" / "a.ts"))
        assert got == "deny", reason

    @pytest.mark.parametrize("fake", [
        {"side_effect": OSError("no git")},
        {"return_value": subprocess.CompletedProcess([], 128, "", "fatal")}],
        ids=["git-missing", "git-fails"])
    def test_GUARD_001_reviewer_is_denied_when_git_cannot_tell(self, fake, repo, monkeypatch):
        monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(repo))  # a fallback root must not stand in for git
        monkeypatch.setattr(lib.subprocess, "run", mock.Mock(**fake))
        got, _ = decide(repo, "casefile:reviewer", "web/a.ts")
        assert got == "deny"


class TestReviewerLimits:
    """GUARD-002: inside a real linked worktree, so a deny here is not GUARD-001's."""

    TOOLS = ("Edit", "Write", "MultiEdit")

    @staticmethod
    def configure(wt, cfg):  # the worktree holds its own copy of the committed settings
        (wt / ".claude").mkdir(exist_ok=True)
        (wt / ".claude" / "casefile.json").write_text(json.dumps(cfg), encoding="utf-8")

    def check(self, repo, wt, paths, decision):
        for path in paths:
            for tool in self.TOOLS:
                got, reason = decide(repo, "casefile:reviewer", str(wt / path), tool=tool, cwd=wt)
                assert got == decision, f"{tool} {path}: {reason}"

    def test_GUARD_002_reviewer_may_not_edit_test_files_in_its_worktree(self, repo, wt):
        paths = ("tests/test_score.py", "worker/app/score_test.py", "web/score.test.ts", "web/e2e/login.spec.ts")
        for p in paths:
            assert TEST_FILE.search(p), p  # the cases are what pre_commit calls a test file
        self.check(repo, wt, paths, "deny")

    def test_GUARD_002_reviewer_may_not_edit_claude_issues_plans_or_specs(self, repo, wt):
        self.check(repo, wt, ("docs/issues/0001-x.md", "docs/plans/M1.md", "docs/specs/10-x.md",
                              ".claude/settings.json"), "deny")

    def test_GUARD_002_plans_and_specs_folders_come_from_config(self, repo, wt):
        self.configure(wt, {"plans_dir": "plans", "specs_dir": "rules", "protected_paths": ["vendor/"]})
        self.check(repo, wt, ("plans/M1.md", "rules/10-x.md", "vendor/lib.js"), "deny")
        self.check(repo, wt, ("docs/plans/M1.md",), "allow")

    def test_GUARD_002_the_defaults_apply_without_configuration(self, repo, wt):
        self.check(repo, wt, ("docs/plans/M1.md", "docs/specs/10-x.md", "docs/issues/0001-x.md"), "deny")

    def test_GUARD_002_reviewer_may_not_edit_protected_paths(self, repo, wt):
        self.configure(wt, {"protected_paths": ["docs/product/", "vendor"]})
        self.check(repo, wt, ("docs/product/blueprint.md", "vendor/lib.js"), "deny")

    def test_GUARD_002_product_code_next_to_them_is_allowed(self, repo, wt):
        self.check(repo, wt, ("web/score.ts", "worker/app/score.py", "README.md", "docs/testing.md"), "allow")

    @pytest.mark.parametrize("tool", ["Edit", "Write"])
    @pytest.mark.parametrize("path", ["tests/test_score.py", "web/score.test.ts"])
    def test_REV_007_reviewer_never_writes_a_test(self, tool, path, repo, wt):
        got, _ = decide(repo, "casefile:reviewer", str(wt / path), tool=tool, cwd=wt)
        assert got == "deny", f"{tool} {path}"


class TestPlanner:
    def test_only_its_plan_file(self, repo):
        expect(repo, ["casefile:planner"], ("docs/plans/M1.md", "docs/plans/saved-jobs.md"), "allow")
        expect(repo, ["casefile:planner"], ("docs/specs/12-matching.md", "web/a.ts",
                                           "docs/plans/sub/x.md", "docs/plans/M1.txt"), "deny")

    def test_plans_dir_from_config(self, repo):
        (repo / ".claude" / "casefile.json").write_text('{"plans_dir": "plans"}', encoding="utf-8")
        expect(repo, ["casefile:planner"], ("plans/M1.md",), "allow")
        expect(repo, ["casefile:planner"], ("docs/plans/M1.md",), "deny")


class TestImplementer:
    def test_writes_code_not_protected_paths(self, repo):
        expect(repo, ["casefile:implementer"], ("web/features/score.ts", "worker/app/parse.py",
                                               "README.md"), "allow")
        expect(repo, ["casefile:implementer"], ("docs/specs/12-matching.md", "docs/product/blueprint.html",
                                               "docs/issues/0001-x.md"), "deny")

    def test_GUARD_006_never_specs_or_plans_even_unprotected(self, bare_repo):
        expect(bare_repo, ["casefile:implementer"], ("docs/plans/M1.md", "docs/specs/12-matching.md"), "deny")
        expect(bare_repo, ["casefile:implementer"], ("docs/plansx/a.md", "web/docs/plans.ts"), "allow")

    def test_GUARD_006_the_folders_come_from_config(self, bare_repo):
        (bare_repo / ".claude").mkdir(exist_ok=True)
        (bare_repo / ".claude" / "casefile.json").write_text(
            '{"plans_dir": "plans", "specs_dir": "rules"}', encoding="utf-8")
        expect(bare_repo, ["casefile:implementer"], ("plans/M1.md", "rules/10-x.md"), "deny")
        expect(bare_repo, ["casefile:implementer"], ("docs/plans/M1.md",), "allow")

    def test_GUARD_006_reason_says_report_blocked(self, bare_repo):
        _, reason = decide(bare_repo, "casefile:implementer", "docs/plans/M1.md")
        assert "STATUS: blocked" in reason, reason

    def test_reason_says_report_blocked(self, repo):
        _, reason = decide(repo, "casefile:implementer", "docs/specs/x.md")
        assert "STATUS: blocked" in reason

    def test_outside_the_repository(self, repo):
        got, reason = decide(repo, "casefile:implementer", os.path.join(tempfile.gettempdir(), "x.txt"))
        assert got == "deny"
        assert "outside" in reason

    def test_paths_in_an_agent_worktree_folder_use_their_repo_path(self, repo):
        wt = repo / ".claude" / "worktrees" / "agent-1"
        expect(repo, ["casefile:implementer"], (str(wt / "docs" / "specs" / "x.md"),), "deny")
        expect(repo, ["casefile:implementer"], (str(wt / "web" / "a.ts"),), "allow")

    def test_inside_a_real_worktree(self, repo, tmp_path):
        commit_empty(repo)
        wt = add_worktree(repo, tmp_path / "wt")
        (wt / ".claude").mkdir(exist_ok=True)
        (wt / ".claude" / "casefile.json").write_text(json.dumps(CONFIG), encoding="utf-8")
        expect(repo, ["casefile:implementer"], (str(wt / "docs" / "specs" / "x.md"),), "deny", cwd=wt)
        expect(repo, ["casefile:implementer"], (str(wt / "web" / "a.ts"),), "allow", cwd=wt)


class TestOtherAgents:
    def test_only_the_claude_rule_applies(self, repo):
        expect(repo, OTHER_AGENTS, ("docs/specs/x.md", "web/a.ts",
                                    os.path.join(tempfile.gettempdir(), "x.txt")), "allow")


class TestNoConfig:
    def test_defaults_protect_claude_and_issues(self, bare_repo):
        expect(bare_repo, ["casefile:implementer"], ("docs/guide.md",), "allow")
        expect(bare_repo, ["casefile:implementer"], (".claude/x.json", "docs/issues/0001-x.md"), "deny")

    def test_issues_are_the_main_sessions_to_write(self, bare_repo):
        expect(bare_repo, [MAIN], ("docs/issues/0001-x.md",), "allow")
        expect(bare_repo, OTHER_AGENTS, ("docs/issues/0001-x.md",), "allow")  # only casefile's rules for casefile agents
        _, reason = decide(bare_repo, "casefile:implementer", "docs/issues/0001-x.md")
        assert "NOTES" in reason


class TestBrokenConfig:
    def test_agents_are_refused_main_is_not(self, repo):
        (repo / ".claude" / "casefile.json").write_text("{ nope", encoding="utf-8")
        got, reason = decide(repo, "casefile:implementer", "web/a.ts")
        assert got == "deny"
        assert ".claude/casefile.json" in reason
        expect(repo, [MAIN], (".claude/casefile.json",), "allow")
