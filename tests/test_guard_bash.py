"""guard_bash: the command rules of the 0.13.0 guard table, for every kind of session."""

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
CASEFILE_AGENTS = ("casefile:reviewer", "casefile:implementer", "casefile:planner")
EVERY_AGENT = OTHER_AGENTS + CASEFILE_AGENTS
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

    def test_every_agent_is_denied(self):
        expect(EVERY_AGENT, self.PUSHES, "deny")

    def test_powershell_push_too(self):
        expect([MAIN], ["git push origin main"], "ask", tool="PowerShell")
        expect(["casefile:implementer"], ["git push"], "deny", tool="PowerShell")

    def test_not_a_push(self):
        expect(EVERYONE, ["git status", "echo git push", "gitpush", "git log --grep push"], "allow")
        # commit and pull are not pushes; casefile's agents are refused them for another reason
        expect((MAIN,) + OTHER_AGENTS,
               ['git commit -m "docs: never git push from agents"',
                "git commit -m 'git push later'", "git pull",
                'git commit -m "fix: x; git push comes later"',
                "git commit -m 'a && git push'"], "allow")

    def test_reasons_say_what_to_do(self):
        _, reason = decide("casefile:implementer", "git push")
        assert "developer" in reason
        _, reason = decide(MAIN, "git push")
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


class TestKillByName:
    KILLS = ("taskkill /IM node.exe /F", "taskkill /f /im node.exe", "pkill -f node", "pkill node",
             "killall node", "Stop-Process -Name node", "Stop-Process -ProcessName node -Force",
             "Get-Process node | Stop-Process")

    def test_agents_may_not_kill_by_name(self):
        expect(EVERY_AGENT, self.KILLS, "deny")

    def test_main_session_may(self):
        expect([MAIN], self.KILLS, "allow")

    def test_killing_one_pid_is_fine(self):
        expect(EVERY_AGENT, ("kill 1234", "taskkill /PID 1234", "Stop-Process -Id 1234"), "allow")


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
            "Set-Content x hi", "sed -i s/a/b/ web/x.ts", "git switch feat", "git cherry-pick abc"),
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
    """GUARD-003 and GUARD-004; GUARD-005: the reviewer restores in the developer's checkout (D-072)."""

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

    def test_GUARD_005_location_does_not_change_other_decisions(self, repo):
        expect(["casefile:planner"], ("git restore web/x.ts",), "deny", cwd=repo)

    def test_GUARD_003_the_reviewer_never_switches_the_checkout(self, repo):
        reviewer_in(repo, ("git switch --detach feat", "git switch feat", "git checkout feat"), "deny")

    def test_GUARD_003_reviewer_may_git_restore_paths(self, repo):
        reviewer_in(repo, (
            "git restore web/x.ts", "git restore -- web/x.ts", "git restore web/a.ts web/b.ts",
            "git restore -- -odd-name.ts"), "allow")

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
        "git restore web/a_b-c@2+x.ts"])
    def test_GUARD_003_listed_flags_are_allowed(self, command, repo):
        reviewer_in(repo, (command,), "allow")

    def test_GUARD_003_other_repository_changes_stay_denied(self, repo):
        reviewer_in(repo, (
            "git add -A", "git commit -m x", "git stash", "git checkout -- web/x.ts", "git reset HEAD~1",
            "rm web/x.ts", "sed -i s/a/b/ web/x.ts", "echo x > web/x.ts",
            "git restore web/x.ts > out.txt", "git restore web/x.ts && npm test"), "deny")

    def test_GUARD_004_planner_may_not_git_restore(self, repo):
        expect(["casefile:reviewer"], ("git restore web/x.ts",), "allow", cwd=repo)
        expect(["casefile:planner"], ("git restore web/x.ts",), "deny", cwd=repo)

    def test_REV_007_reviewer_never_commits(self, repo):
        reviewer_in(repo, ("git commit -m x", "git commit -am x", "git add -A"), "deny")


class TestImplementer:
    def test_works_in_the_checkout(self):
        expect(["casefile:implementer"], (
            "git add -A", "npm test", "git status", "git diff", "git log --oneline -5",
            "git restore web/x.ts", "npm install zod", "uv add httpx", "rm web/old.ts"), "allow")

    def test_GUARD_008_never_commits_or_moves_a_ref(self):
        expect(["casefile:implementer"], (
            "git commit -m 'feat(M1/T1): x [MATCH-010]'", "git commit -am x", "git merge main",
            "git rebase main", "git cherry-pick abc", "git revert HEAD", "git reset HEAD~1",
            "git reset --hard HEAD~1", "git stash", "git stash pop", "git switch -c fix/x",
            "git switch main", "git checkout main", "git checkout -- web/x.ts",
            "git update-ref refs/heads/x HEAD", "git tag v1", "git branch -D feat"), "deny")

    def test_GUARD_008_reason_says_the_orchestrator_commits(self):
        _, reason = decide("casefile:implementer", "git commit -m x")
        assert "orchestrator" in reason and "uncommitted" in reason


class TestOneCommandPerCall:
    def test_casefile_agents_never_chain(self):
        expect(CASEFILE_AGENTS, (
            "npm run typecheck | tail; npm run lint | tail; git commit -m x", "cd web && npm test",
            "npm test || true", "npm test\nnpm run lint", "npx playwright test e2e | tail -20"), "deny")

    def test_one_command_quoted_separators_and_other_pipes_pass(self):
        expect(CASEFILE_AGENTS, ('git log --grep "a; b && c"', "git log --oneline | head -5",
                                "timeout 300 npm test"), "allow")
        expect((MAIN,) + OTHER_AGENTS, ("npm test && npm run lint",), "allow")


class TestNoWaitLoops:
    def test_casefile_agents_do_not_poll(self):
        expect(CASEFILE_AGENTS, (
            "sleep 100; cat out.log", "until grep -q done out.log; do sleep 5; done",
            "while true; do cat x; done", "sleep 1m", "Start-Sleep -Seconds 60"), "deny")

    def test_a_short_pause_and_everyone_else_pass(self):
        expect(CASEFILE_AGENTS, ("sleep 2", "timeout 120 npm test"), "allow")
        expect((MAIN,) + OTHER_AGENTS, ("sleep 100", "until false; do sleep 5; done"), "allow")


class TestPlanner:
    def test_reads_only(self):
        expect(["casefile:planner"], ("git log --oneline", "git status", "ls docs"), "allow")
        expect(["casefile:planner"], ("git commit -m x", "rm x", "echo x > plan.md"), "deny")


class TestOthersUnrestricted:
    def test_main_and_other_agents(self):
        expect((MAIN,) + OTHER_AGENTS, ("git merge feat", "git reset --hard", "rm -rf build",
                                        "echo hi > x.txt"), "allow")


class TestRobustness:
    def test_no_command(self):
        code, out = run.dispatch("guard_bash", json.dumps({"hook_event_name": "PreToolUse",
                                                           "tool_name": "Bash", "tool_input": {}}))
        assert (code, out) == (0, "")
