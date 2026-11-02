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
# Agents with no rules of their own (GUARD-009): any agent but the reviewer, casefile names included.
PLAIN_AGENTS = OTHER_AGENTS + ("casefile:implementer", "casefile:planner")

CONFIG = {"protected_paths": ["docs/specs/", "docs/product/", "docs/issues/"]}


def make_repo(root, config):
    root.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=root, check=True)
    if config is not None:
        (root / ".claude").mkdir()
        (root / ".claude" / "casefile.json").write_text(json.dumps(config), encoding="utf-8")
    return root


@pytest.fixture
def repo(tmp_path):
    return make_repo(tmp_path / "repo", CONFIG)


@pytest.fixture
def bare_repo(tmp_path):
    """A repository with no `.claude/casefile.json`."""
    return make_repo(tmp_path / "repo", None)


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


class TestReviewer:
    def test_GUARD_002_writes_no_records_in_the_checkout(self, repo):
        expect(repo, ["casefile:reviewer"], ("docs/plans/M1.md", "docs/issues/0001-x.md"), "deny")


EDITS = (("Write", "web/a.ts"), ("NotebookEdit", "nb.ipynb"), ("Write", "web/new-folder/b.ts"))


class TestReviewerCheckout:
    """GUARD-001: the reviewer breaks code in the developer's checkout (D-072)."""

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
    """GUARD-002: in the checkout, where GUARD-001 allows the reviewer's product-code edits, so a deny here
    is GUARD-002's."""

    @staticmethod
    def configure(repo, cfg):
        (repo / ".claude").mkdir(exist_ok=True)
        (repo / ".claude" / "casefile.json").write_text(json.dumps(cfg), encoding="utf-8")

    def check(self, repo, paths, decision):
        for path in paths:
            got, reason = decide(repo, "casefile:reviewer", path)
            assert got == decision, f"{path}: {reason}"

    def test_REV_007_GUARD_002_reviewer_may_not_edit_test_files(self, repo):
        paths = ("tests/test_score.py", "worker/app/score_test.py", "web/score.test.ts", "web/e2e/login.spec.ts")
        for p in paths:
            assert TEST_FILE.search(p), p  # the cases are what pre_commit calls a test file
        self.check(repo, paths, "deny")

    def test_GUARD_002_reviewer_may_not_edit_claude_issues_plans_or_specs(self, repo):
        self.check(repo, ("docs/issues/0001-x.md", "docs/plans/M1.md", "docs/specs/10-x.md",
                          ".claude/settings.json"), "deny")

    def test_GUARD_002_plans_and_specs_folders_come_from_config(self, repo):
        self.configure(repo, {"plans_dir": "plans", "specs_dir": "rules", "protected_paths": ["vendor/"]})
        self.check(repo, ("plans/M1.md", "rules/10-x.md", "vendor/lib.js"), "deny")
        self.check(repo, ("docs/plans/M1.md",), "allow")

    def test_GUARD_002_the_defaults_apply_without_configuration(self, bare_repo):
        self.check(bare_repo, ("docs/plans/M1.md", "docs/specs/10-x.md", "docs/issues/0001-x.md"), "deny")

    def test_GUARD_002_reviewer_may_not_edit_protected_paths(self, repo):
        self.configure(repo, {"protected_paths": ["docs/product/", "vendor"]})
        self.check(repo, ("docs/product/blueprint.md", "vendor/lib.js"), "deny")

    def test_GUARD_002_product_code_next_to_them_is_allowed(self, repo):
        self.check(repo, ("web/score.ts", "worker/app/score.py", "README.md", "docs/testing.md"), "allow")


class TestNoAgentOnlyRules:
    """GUARD-009: any agent but the reviewer writes where the main session may."""

    def test_GUARD_009_an_agent_writes_where_the_main_session_may(self, repo):
        paths = (".claude/settings.json", os.path.join(os.path.expanduser("~"), ".claude", "settings.json"),
                 "docs/specs/12-matching.md", "docs/plans/M1.md", "docs/issues/0001-x.md",
                 "docs/product/blueprint.md", "web/a.ts", os.path.join(tempfile.gettempdir(), "x.txt"))
        expect(repo, (MAIN,) + PLAIN_AGENTS, paths, "allow")

    def test_GUARD_009_with_or_without_configuration(self, bare_repo):
        expect(bare_repo, PLAIN_AGENTS, ("docs/plans/M1.md", "docs/issues/0001-x.md", ".claude/x.json"), "allow")


class TestBrokenConfig:
    def test_the_reviewer_is_refused_others_are_not(self, repo):
        (repo / ".claude" / "casefile.json").write_text("{ nope", encoding="utf-8")
        got, reason = decide(repo, "casefile:reviewer", "web/a.ts")
        assert got == "deny"
        assert ".claude/casefile.json" in reason
        expect(repo, (MAIN,) + PLAIN_AGENTS, (".claude/casefile.json", "web/a.ts"), "allow")
