"""The shared hook library: reading events, decisions, who is acting, paths, config."""

import io
import json
import os
import pathlib
import subprocess
import sys
from contextlib import redirect_stdout
from unittest import mock

import pytest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "hooks"))

from casefile_hooks import lib

FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


def exits(fn, *args) -> tuple[str, int]:
    """Run a decision function that must exit; return what it printed and its exit code."""
    out = io.StringIO()
    with redirect_stdout(out), pytest.raises(SystemExit) as caught:
        fn(*args)
    return out.getvalue(), caught.value.code or 0


def decision_of(fn, *args) -> dict:
    """Run a decision function, check it exits 0, and return the JSON it printed."""
    printed, code = exits(fn, *args)
    assert code == 0, code
    return json.loads(printed)


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, timeout=60)


def stdin_of(raw: bytes):
    return mock.patch.object(sys, "stdin", io.TextIOWrapper(io.BytesIO(raw), encoding="utf-8"))


@pytest.mark.parametrize("path", sorted(FIXTURES.glob("*.json")), ids=lambda p: p.name)
def test_every_fixture_parses(path):
    with stdin_of(path.read_bytes()):
        event = lib.read_event()
    assert "hook_event_name" in event, path.name


def test_bad_json_raises():
    with stdin_of(b"{not json"), pytest.raises(ValueError):
        lib.read_event()


def test_empty_input_raises():
    with stdin_of(b""), pytest.raises(ValueError):
        lib.read_event()


def test_non_ascii_path_survives():
    raw = json.dumps({"hook_event_name": "PreToolUse", "cwd": "C:\\Usuários\\joão"}, ensure_ascii=False)
    with stdin_of(raw.encode("utf-8")):
        assert lib.read_event()["cwd"] == "C:\\Usuários\\joão"


def test_deny():
    out = decision_of(lib.deny, "no pushing from agents")
    assert out == {"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": "casefile: no pushing from agents",
    }}


def test_ask():
    out = decision_of(lib.ask, "push to the remote?")
    assert out["hookSpecificOutput"]["permissionDecision"] == "ask"
    assert out["hookSpecificOutput"]["permissionDecisionReason"] == "casefile: push to the remote?"


def test_allow_prints_nothing():
    assert exits(lib.allow) == ("", 0)


def test_main_session_is_none():
    assert lib.agent_of(fixture("bash_main")) is None
    assert lib.agent_of(fixture("bash_main_auto")) is None
    assert lib.agent_of(fixture("powershell_main")) is None


def test_plugin_agent():
    assert lib.agent_of(fixture("bash_plugin_agent")) == "casefile:reviewer"


def test_builtin_agent():
    assert lib.agent_of(fixture("bash_builtin_agent")) == "Explore"


def test_casefile_agent_name():
    assert lib.casefile_agent(fixture("bash_plugin_agent")) == "reviewer"
    assert lib.casefile_agent(fixture("bash_builtin_agent")) is None
    assert lib.casefile_agent(fixture("bash_main")) is None


@pytest.fixture
def repo_in(tmp_path):
    """tmp_path holds a repository at tmp_path/repo with one empty commit."""
    repo = tmp_path / "repo"
    repo.mkdir()
    git("init", "-q", cwd=repo)
    git("-c", "user.email=t@t", "-c", "user.name=t", "commit", "-q", "--allow-empty", "-m", "init", cwd=repo)
    return repo


def same(a, b):
    assert os.path.normcase(os.path.realpath(a)) == os.path.normcase(os.path.realpath(b))


def test_git_root(repo_in):
    (repo_in / "web").mkdir()
    same(lib.git_root(str(repo_in / "web")), repo_in)


def test_git_root_outside_a_repo(tmp_path):
    assert lib.git_root(str(tmp_path)) is None


def test_relative_and_absolute_paths(repo_in):
    event = {"cwd": str(repo_in)}
    assert lib.repo_relative(event, "web/a.ts") == "web/a.ts"
    assert lib.repo_relative(event, str(repo_in / "web" / "a.ts")) == "web/a.ts"


def test_path_into_an_agent_worktree_folder(repo_in):
    event = {"cwd": str(repo_in)}
    path = repo_in / ".claude" / "worktrees" / "agent-1" / "web" / "a.ts"
    assert lib.repo_relative(event, str(path)) == "web/a.ts"


def test_inside_a_real_worktree(repo_in, tmp_path):
    wt = tmp_path / "wt"
    git("worktree", "add", "-q", str(wt), cwd=repo_in)
    event = {"cwd": str(wt)}
    assert lib.repo_relative(event, str(wt / "docs" / "x.md")) == "docs/x.md"


def test_outside_the_repo(repo_in, tmp_path):
    event = {"cwd": str(repo_in)}
    assert lib.repo_relative(event, str(tmp_path / "elsewhere.txt")) is None


def test_no_path(repo_in):
    assert lib.repo_relative({"cwd": str(repo_in)}, None) is None


@pytest.fixture
def config_repo(tmp_path):
    git("init", "-q", cwd=tmp_path)
    return tmp_path


def write_config(repo, text: str):
    (repo / ".claude").mkdir(exist_ok=True)
    (repo / ".claude" / "casefile.json").write_text(text, encoding="utf-8")


def test_no_file_gives_defaults(config_repo):
    cfg = lib.config({"cwd": str(config_repo)})
    assert cfg["default_branch"] == "main"
    assert cfg["protected_paths"] == []
    assert cfg["apps"] == {}
    assert cfg["design"].get("tokens") == "docs/product/design-system/tokens.json"
    assert cfg["design"].get("ui_paths") == []
    assert cfg["build_order"] == "docs/product/blueprint.html"


def test_partial_file_keeps_other_defaults(config_repo):
    write_config(config_repo, '{"protected_paths": ["docs/specs/"], "design": {"ui_paths": ["web/"]}}')
    cfg = lib.config({"cwd": str(config_repo)})
    assert cfg["protected_paths"] == ["docs/specs/"]
    assert cfg["default_branch"] == "main"
    assert cfg["design"].get("ui_paths") == ["web/"]
    assert cfg["design"].get("tokens") == "docs/product/design-system/tokens.json"


def test_invalid_json_names_the_file(config_repo):
    write_config(config_repo, "{ nope")
    with pytest.raises(lib.ConfigError) as caught:
        lib.config({"cwd": str(config_repo)})
    assert ".claude/casefile.json" in str(caught.value)


def test_old_devflow_file_is_refused_not_ignored(config_repo):
    (config_repo / ".claude").mkdir()
    (config_repo / ".claude" / "devflow.json").write_text('{"protected_paths": ["docs/"]}', encoding="utf-8")
    with pytest.raises(lib.ConfigError) as caught:
        lib.config({"cwd": str(config_repo)})
    assert "rename it to .claude/casefile.json" in str(caught.value)


def test_wrong_type_names_the_key(config_repo):
    write_config(config_repo, '{"protected_paths": "docs/"}')
    with pytest.raises(lib.ConfigError) as caught:
        lib.config({"cwd": str(config_repo)})
    assert "protected_paths" in str(caught.value)


def test_outside_a_repo_gives_defaults(tmp_path):
    write_config(tmp_path, '{"apps": {"web": {"test": "npm test"}}}')  # not read: no repository here
    assert lib.config({"cwd": str(tmp_path)})["apps"] == {}
