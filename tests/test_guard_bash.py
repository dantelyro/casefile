"""guard_bash: the command rules for every session alike, and the reviewer's own (GUARD-009)."""

import json
import pathlib
import subprocess
import sys
from unittest import mock

import pytest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run
from casefile_hooks import lib

MAIN = None
OTHER_AGENTS = ("Explore", "general-purpose", "other-plugin:helper")
# Agents with no rules of their own (GUARD-009): any agent but the reviewer, casefile names included.
PLAIN_AGENTS = OTHER_AGENTS + ("casefile:implementer", "casefile:planner")
EVERY_AGENT = PLAIN_AGENTS + ("casefile:reviewer",)
EVERYONE = (MAIN,) + EVERY_AGENT


def event(agent, command, tool="Bash", cwd=None):
    e = json.loads((FIXTURES / "bash_main.json").read_text(encoding="utf-8"))
    e["tool_name"] = tool
    e["tool_input"] = {"command": command}
    if cwd:
        e["cwd"] = str(cwd)
    e.pop("agent_type", None)
    if agent:
        e["agent_type"] = agent
        e["agent_id"] = "a1"
    return e


def decide(agent, command, tool="Bash", cwd=None):
    """'allow', 'ask' or 'deny', plus the reason."""
    code, out = run.dispatch("guard_bash", json.dumps(event(agent, command, tool, cwd)))
    assert code == 0, (code, out)
    if not out:
        return "allow", ""
    hso = json.loads(out)["hookSpecificOutput"]
    return hso["permissionDecision"], hso["permissionDecisionReason"]


def expect(agents, commands, decision, tool="Bash", cwd=None):
    for agent in agents:
        for command in commands:
            got, reason = decide(agent, command, tool, cwd)
            assert got == decision, f"{agent!r}: {command!r} → {got}: {reason}"


class TestPush:
    PUSHES = ("git push", "git push origin main", "git push --force", "cd web && git push",
              "git status; git push", "git -C ../other push origin x", "git --no-pager push",
              "npm test\ngit push", "git status | tee x; git push", "{ git push; }",
              "if ($?) { git push }", "(git push)", "  git   push  ")

    def test_main_session_is_asked(self):
        expect([MAIN], self.PUSHES, "ask")

    def test_GUARD_009_every_agent_is_asked_like_the_main_session(self):
        expect(EVERY_AGENT, self.PUSHES, "ask")

    def test_powershell_push_too(self):
        expect([MAIN], ["git push origin main"], "ask", tool="PowerShell")
        expect(["casefile:implementer"], ["git push"], "ask", tool="PowerShell")

    def test_not_a_push(self):
        expect(EVERYONE, ["git status", "echo git push", "gitpush", "git log --grep push"], "allow")
        # commit and pull are not pushes; the reviewer is refused them for another reason
        expect((MAIN,) + PLAIN_AGENTS,
               ['git commit -m "docs: never git push from agents"',
                "git commit -m 'git push later'", "git pull",
                'git commit -m "fix: x; git push comes later"',
                "git commit -m 'a && git push'"], "allow")

    def test_reasons_say_what_to_do(self):
        for who in (MAIN, "casefile:implementer"):
            _, reason = decide(who, "git push")
            assert "push" in reason


class TestComposeVolumes:
    def test_nobody_removes_compose_volumes(self):
        expect(EVERYONE, ("docker compose down -v", "docker compose down --volumes",
                          "docker-compose down -v", "docker compose -p m1t13 down -v",
                          "docker compose down --remove-orphans -v", "docker compose down -vt 5",
                          "cd web; docker compose down -v; cd .."), "deny")

    def test_other_compose_commands_pass(self):
        expect(EVERYONE, ("docker compose down", "docker compose down --remove-orphans",
                          "docker compose up -d --build --wait", "docker compose build web",
                          "docker run -v pgdata:/var/lib/postgresql/data postgres:16"), "allow")


class TestNoVerify:
    def test_nobody_skips_git_hooks(self):
        expect(EVERYONE, ("git commit --no-verify -m x", "git push --no-verify",
                          "git -C web commit -m x --no-verify", "git merge --no-verify feat"), "deny")

    def test_mentioning_it_is_fine(self):
        expect([MAIN], ['git commit -m "never use --no-verify"', "grep -r no-verify docs"], "allow")


class TestReviewer:
    def test_reads_and_tests(self):
        expect(["casefile:reviewer"], (
            "git diff main...feat", "git log --oneline -5", "git show HEAD", "git status",
            "npm test 2>&1", "uv run pytest -q", "npm ci",
            "uv sync", "npm test > /dev/null", "npm test 2>/dev/null", "git branch --list"), "allow")

    def test_changes_nothing(self):
        expect(["casefile:reviewer"], (
            "git add -A", "git commit -m x", "git merge feat", "git rebase main", "git reset HEAD~1",
            "git stash", "git checkout -- web/x.ts", "git branch -d feat",
            "rm web/x.ts", "mv a b", "echo hi > notes.txt", "cat x >> y", "Remove-Item x",
            "Set-Content x hi", "sed -i s/a/b/ web/x.ts", "git switch feat", "git cherry-pick abc",
            "git commit -am x", "echo x > web/x.ts", "git restore web/x.ts > out.txt",
            "git restore web/x.ts && npm test"),
            "deny")


@pytest.fixture
def repo(tmp_path):
    """The developer's checkout, where the reviewer works."""
    path = tmp_path / "repo"
    path.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=path, check=True)
    return path


def reviewer_in(repo, commands, decision):
    expect(["casefile:reviewer"], commands, decision, cwd=repo)


class TestRestore:
    """GUARD-003; GUARD-005: the reviewer restores in the developer's checkout (D-072)."""

    def test_GUARD_005_reviewer_restore_allowed_in_the_checkout(self, repo):
        expect(["casefile:reviewer"], ("git restore web/x.ts",), "allow", cwd=repo)
        (repo / "web").mkdir()
        expect(["casefile:reviewer"], ("git restore web/x.ts",), "allow", cwd=repo / "web")

    def test_GUARD_005_reviewer_restore_denied_outside_any_repository(self, tmp_path):
        outside = tmp_path / "plain"
        outside.mkdir()
        got, reason = decide("casefile:reviewer", "git restore web/x.ts", cwd=outside)
        assert got == "deny", reason
        assert "repository" in reason

    @pytest.mark.parametrize("failing", [
        mock.Mock(side_effect=OSError("no git")),
        mock.Mock(return_value=mock.Mock(returncode=128, stdout="", stderr="fatal")),
    ], ids=["git-missing", "git-fails"])
    def test_GUARD_005_reviewer_restore_denied_when_git_cannot_tell(self, failing, repo, monkeypatch):
        monkeypatch.setattr(lib.subprocess, "run", failing)
        got, reason = decide("casefile:reviewer", "git restore web/x.ts", cwd=repo)
        assert got == "deny", reason

    def test_GUARD_003_the_reviewer_never_switches_the_checkout(self, repo):
        reviewer_in(repo, ("git switch --detach feat", "git switch feat", "git checkout feat"), "deny")

    def test_GUARD_003_restore_without_a_path_is_denied(self, repo):
        reviewer_in(repo, ("git restore", "git restore --"), "deny")

    def test_GUARD_003_restore_with_staged_or_source_is_denied(self, repo):
        reviewer_in(repo, (
            "git restore --staged web/x.ts", "git restore -S web/x.ts",
            "git restore --source HEAD~1 web/x.ts", "git restore -s HEAD~1 web/x.ts",
            "git restore --source=HEAD~1 web/x.ts", "git restore -sHEAD~1 web/x.ts",
            "git restore -SW web/x.ts", "git restore --stag web/x.ts",
            "git restore --sou=HEAD~1 web/x.ts", "git restore --so HEAD~1 web/x.ts",
            'git restore "--staged" web/x.ts', "git restore '-s' HEAD~1 web/x.ts",
            'git restore --sta""ged web/x.ts'), "deny")

    @pytest.mark.parametrize("command", [
        r"git restore --st\aged web/x.ts", "git restore $'--staged' web/x.ts",
        "git restore web/x.ts --$(echo staged)", "git -C ../other restore web/x.ts",
        "git restore --ours web/x.ts", "git restore web/x.ts `echo --staged`",
        "git --git-dir=../o/.git restore web/x.ts", "git restore -Wq web/x.ts",
        "git restore web/x.ts <(echo hi)", "git restore web/x.ts {--staged,}",
        "git restore web/x.ts *", "git restore ~/x.ts", "git restore web/x.ts !!",
        "git restore 'web/a(1).ts'", 'git restore "web/$x.ts"',
        "git restore web/x.ts ?", "git restore web/[xy].ts", "git restore web/x.ts #c",
        "git restore -W web/x.ts", "git restore --worktree web/x.ts"])
    def test_GUARD_003_shell_escapes_other_flags_and_git_options_are_denied(self, command, repo):
        reviewer_in(repo, (command,), "deny")

    @pytest.mark.parametrize("command", [
        "git restore -q -- web/x.ts", "git restore --patch --quiet web/x.ts", "git restore -p web/x.ts",
        'git restore "web/my file.ts"', "git restore -p -q -- web/x.ts",
        "git restore web/a_b-c@2+x.ts", "git restore -- web/x.ts", "git restore web/a.ts web/b.ts",
        "git restore -- -odd-name.ts"])
    def test_GUARD_003_listed_flags_are_allowed(self, command, repo):
        reviewer_in(repo, (command,), "allow")



class TestNoAgentOnlyRules:
    """GUARD-009: an agent's call is judged as the main session's would be; only the reviewer has rules."""

    SAME_AS_MAIN = (
        "taskkill /IM node.exe /F", "pkill -f node", "killall node", "Stop-Process -Name node",
        "cd web && npm test", "npm test || true", "npm test\nnpm run lint", "npx playwright test e2e | tail -20",
        "sleep 100; cat out.log", "until grep -q done out.log; do sleep 5; done", "Start-Sleep -Seconds 60",
        "git commit -m x", "git merge feat", "git reset --hard HEAD~1", "git stash", "git switch main",
        "git update-ref refs/heads/x HEAD", "git branch -D feat", "rm -rf build", "echo hi > x.txt")

    def test_GUARD_009_an_agent_is_allowed_what_the_main_session_is(self):
        for command in self.SAME_AS_MAIN:
            main = decide(MAIN, command)[0]
            assert main == "allow", command
            for agent in PLAIN_AGENTS:
                assert decide(agent, command)[0] == main, f"{agent!r}: {command!r}"

    def test_GUARD_009_and_denied_what_it_is_denied(self):
        expect(PLAIN_AGENTS, ("docker compose down -v", "git commit --no-verify -m x"), "deny")

    def test_GUARD_009_the_reviewer_keeps_its_own_rules(self):
        expect(["casefile:reviewer"], ("git commit -m x", "rm x", "echo x > y"), "deny")


class TestRobustness:
    def test_no_command(self):
        code, out = run.dispatch("guard_bash", json.dumps({"hook_event_name": "PreToolUse",
                                                           "tool_name": "Bash", "tool_input": {}}))
        assert (code, out) == (0, "")
