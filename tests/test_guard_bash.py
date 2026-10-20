"""guard_bash: the command rules of the 0.13.0 guard table, for every kind of session."""

import json
import pathlib
import sys
import unittest

HOOKS = pathlib.Path(__file__).resolve().parent.parent / "hooks"
FIXTURES = pathlib.Path(__file__).resolve().parent / "fixtures"
sys.path.insert(0, str(HOOKS))

import run  # noqa: E402

MAIN = None
OTHER_AGENTS = ("Explore", "general-purpose", "other-plugin:helper")
DEVFLOW_AGENTS = ("devflow:reviewer", "devflow:implementer", "devflow:planner")
EVERY_AGENT = OTHER_AGENTS + DEVFLOW_AGENTS
EVERYONE = (MAIN,) + EVERY_AGENT


def event(agent, command, tool="Bash"):
    e = json.loads((FIXTURES / "bash_main.json").read_text(encoding="utf-8"))
    e["tool_name"] = tool
    e["tool_input"] = {"command": command}
    e.pop("agent_type", None)
    if agent:
        e["agent_type"] = agent
        e["agent_id"] = "a1"
    return e


def decide(agent, command, tool="Bash"):
    """'allow', 'ask' or 'deny', plus the reason."""
    code, out = run.dispatch("guard_bash", json.dumps(event(agent, command, tool)))
    assert code == 0, (code, out)
    if not out:
        return "allow", ""
    hso = json.loads(out)["hookSpecificOutput"]
    return hso["permissionDecision"], hso["permissionDecisionReason"]


class Base(unittest.TestCase):
    def expect(self, agents, commands, decision, tool="Bash"):
        for agent in agents:
            for command in commands:
                got, reason = decide(agent, command, tool)
                self.assertEqual(got, decision, f"{agent!r}: {command!r} → {got}: {reason}")


class Push(Base):
    PUSHES = ("git push", "git push origin main", "git push --force", "cd web && git push",
              "git status; git push", "git -C ../other push origin x", "git --no-pager push",
              "npm test\ngit push", "git status | tee x; git push", "{ git push; }",
              "if ($?) { git push }", "(git push)", "  git   push  ")

    def test_main_session_is_asked(self):
        self.expect([MAIN], self.PUSHES, "ask")

    def test_every_agent_is_denied(self):
        self.expect(EVERY_AGENT, self.PUSHES, "deny")

    def test_powershell_push_too(self):
        self.expect([MAIN], ["git push origin main"], "ask", tool="PowerShell")
        self.expect(["devflow:implementer"], ["git push"], "deny", tool="PowerShell")

    def test_not_a_push(self):
        self.expect(EVERYONE, ["git status", "echo git push", "gitpush", "git log --grep push"], "allow")
        # commit and pull are not pushes; the read-only agents are refused them for another reason
        self.expect((MAIN, "devflow:implementer") + OTHER_AGENTS,
                    ['git commit -m "docs: never git push from agents"',
                     "git commit -m 'git push later'", "git pull",
                     'git commit -m "fix: x; git push comes later"',
                     "git commit -m 'a && git push'"], "allow")

    def test_reasons_say_what_to_do(self):
        _, reason = decide("devflow:implementer", "git push")
        self.assertIn("developer", reason)
        _, reason = decide(MAIN, "git push")
        self.assertIn("push", reason)


class ComposeVolumes(Base):
    def test_nobody_removes_compose_volumes(self):
        self.expect(EVERYONE, ("docker compose down -v", "docker compose down --volumes",
                               "docker-compose down -v", "docker compose -p m1t13 down -v",
                               "docker compose down --remove-orphans -v", "docker compose down -vt 5",
                               "cd web; docker compose down -v; cd .."), "deny")

    def test_other_compose_commands_pass(self):
        self.expect(EVERYONE, ("docker compose down", "docker compose down --remove-orphans",
                               "docker compose up -d --build --wait", "docker compose build web",
                               "docker run -v pgdata:/var/lib/postgresql/data postgres:16"), "allow")


class NoVerify(Base):
    def test_nobody_skips_git_hooks(self):
        self.expect(EVERYONE, ("git commit --no-verify -m x", "git push --no-verify",
                               "git -C web commit -m x --no-verify", "git merge --no-verify feat"), "deny")

    def test_mentioning_it_is_fine(self):
        self.expect([MAIN], ['git commit -m "never use --no-verify"', "grep -r no-verify docs"], "allow")


class KillByName(Base):
    KILLS = ("taskkill /IM node.exe /F", "taskkill /f /im node.exe", "pkill -f node", "pkill node",
             "killall node", "Stop-Process -Name node", "Stop-Process -ProcessName node -Force",
             "Get-Process node | Stop-Process")

    def test_agents_may_not_kill_by_name(self):
        self.expect(EVERY_AGENT, self.KILLS, "deny")

    def test_main_session_may(self):
        self.expect([MAIN], self.KILLS, "allow")

    def test_killing_one_pid_is_fine(self):
        self.expect(EVERY_AGENT, ("kill 1234", "taskkill /PID 1234", "Stop-Process -Id 1234"), "allow")


class Reviewer(Base):
    def test_reads_and_tests(self):
        self.expect(["devflow:reviewer"], (
            "git diff main...feat", "git log --oneline -5", "git show HEAD", "git status",
            "git switch --detach feat", "npm test 2>&1", "uv run pytest -q", "npm ci",
            "uv sync", "npm test > /dev/null", "npm test 2>/dev/null", "git branch --list"), "allow")

    def test_changes_nothing(self):
        self.expect(["devflow:reviewer"], (
            "git add -A", "git commit -m x", "git merge feat", "git rebase main", "git reset HEAD~1",
            "git stash", "git checkout -- web/x.ts", "git branch -d feat",
            "rm web/x.ts", "mv a b", "echo hi > notes.txt", "cat x >> y", "Remove-Item x",
            "Set-Content x hi", "sed -i s/a/b/ web/x.ts", "git switch feat", "git cherry-pick abc"),
            "deny")


class Restore(Base):
    def test_GUARD_003_reviewer_may_git_restore_paths(self):
        self.expect(["devflow:reviewer"], (
            "git restore web/x.ts", "git restore -- web/x.ts", "git restore web/a.ts web/b.ts",
            "git restore -- -odd-name.ts"), "allow")

    def test_GUARD_003_restore_without_a_path_is_denied(self):
        self.expect(["devflow:reviewer"], ("git restore", "git restore --"), "deny")

    def test_GUARD_003_restore_with_staged_or_source_is_denied(self):
        self.expect(["devflow:reviewer"], (
            "git restore --staged web/x.ts", "git restore -S web/x.ts",
            "git restore --source HEAD~1 web/x.ts", "git restore -s HEAD~1 web/x.ts",
            "git restore --source=HEAD~1 web/x.ts", "git restore -sHEAD~1 web/x.ts",
            "git restore -SW web/x.ts", "git restore --stag web/x.ts",
            "git restore --sou=HEAD~1 web/x.ts", "git restore --so HEAD~1 web/x.ts",
            'git restore "--staged" web/x.ts', "git restore '-s' HEAD~1 web/x.ts",
            'git restore --sta""ged web/x.ts'), "deny")

    def test_GUARD_003_shell_escapes_other_flags_and_git_options_are_denied(self):
        for command in (r"git restore --st\aged web/x.ts", "git restore $'--staged' web/x.ts",
                        "git restore web/x.ts --$(echo staged)", "git -C ../other restore web/x.ts",
                        "git restore --ours web/x.ts", "git restore web/x.ts `echo --staged`",
                        "git --git-dir=../o/.git restore web/x.ts", "git restore -Wq web/x.ts",
                        "git restore web/x.ts <(echo hi)", "git restore web/x.ts {--staged,}",
                        "git restore web/x.ts *", "git restore ~/x.ts", "git restore web/x.ts !!",
                        "git restore 'web/a(1).ts'", 'git restore "web/$x.ts"',
                        "git restore web/x.ts ?", "git restore web/[xy].ts", "git restore web/x.ts #c"):
            with self.subTest(command=command):
                self.expect(["devflow:reviewer"], (command,), "deny")

    def test_GUARD_003_listed_flags_are_allowed(self):
        for command in ("git restore -W web/x.ts", "git restore -q -- web/x.ts",
                        "git restore --worktree --quiet web/x.ts", "git restore -p web/x.ts",
                        'git restore "web/my file.ts"', "git restore -W -q -- web/x.ts",
                        "git restore web/a_b-c@2+x.ts"):
            with self.subTest(command=command):
                self.expect(["devflow:reviewer"], (command,), "allow")

    def test_GUARD_003_other_repository_changes_stay_denied(self):
        self.expect(["devflow:reviewer"], (
            "git add -A", "git commit -m x", "git stash", "git checkout -- web/x.ts", "git reset HEAD~1",
            "rm web/x.ts", "sed -i s/a/b/ web/x.ts", "echo x > web/x.ts",
            "git restore web/x.ts > out.txt", "git restore web/x.ts && npm test"), "deny")

    def test_GUARD_004_planner_may_not_git_restore(self):
        self.expect(["devflow:reviewer"], ("git restore web/x.ts",), "allow")
        self.expect(["devflow:planner"], ("git restore web/x.ts",), "deny")

    def test_REV_007_reviewer_never_commits(self):
        self.expect(["devflow:reviewer"], ("git commit -m x", "git commit -am x", "git add -A"), "deny")


class Implementer(Base):
    def test_works_on_its_branch(self):
        self.expect(["devflow:implementer"], (
            "git add -A", "git commit -m 'feat(M1/T1): x [MATCH-010]'", "npm test", "git status",
            "npm install zod", "uv add httpx", "git switch -c fix/x", "rm web/old.ts"), "allow")

    def test_does_not_merge_rewrite_or_touch_the_default_branch(self):
        self.expect(["devflow:implementer"], (
            "git merge main", "git rebase main", "git cherry-pick abc", "git reset --hard HEAD~1",
            "git switch main", "git checkout main", "git branch -D feat"), "deny")


class OneCommandPerCall(Base):
    def test_devflow_agents_never_chain(self):
        self.expect(DEVFLOW_AGENTS, (
            "npm run typecheck | tail; npm run lint | tail; git commit -m x", "cd web && npm test",
            "npm test || true", "npm test\nnpm run lint", "npx playwright test e2e | tail -20"), "deny")

    def test_one_command_quoted_separators_and_other_pipes_pass(self):
        self.expect(DEVFLOW_AGENTS, ('git log --grep "a; b && c"', "git log --oneline | head -5",
                                     "timeout 300 npm test"), "allow")
        self.expect((MAIN,) + OTHER_AGENTS, ("npm test && npm run lint",), "allow")


class NoWaitLoops(Base):
    def test_devflow_agents_do_not_poll(self):
        self.expect(DEVFLOW_AGENTS, (
            "sleep 100; cat out.log", "until grep -q done out.log; do sleep 5; done",
            "while true; do cat x; done", "sleep 1m", "Start-Sleep -Seconds 60"), "deny")

    def test_a_short_pause_and_everyone_else_pass(self):
        self.expect(DEVFLOW_AGENTS, ("sleep 2", "timeout 120 npm test"), "allow")
        self.expect((MAIN,) + OTHER_AGENTS, ("sleep 100", "until false; do sleep 5; done"), "allow")


class Planner(Base):
    def test_reads_only(self):
        self.expect(["devflow:planner"], ("git log --oneline", "git status", "ls docs"), "allow")
        self.expect(["devflow:planner"], ("git commit -m x", "rm x", "echo x > plan.md"), "deny")


class OthersUnrestricted(Base):
    def test_main_and_other_agents(self):
        self.expect((MAIN,) + OTHER_AGENTS, ("git merge feat", "git reset --hard", "rm -rf build",
                                             "echo hi > x.txt"), "allow")


class Robustness(Base):
    def test_no_command(self):
        code, out = run.dispatch("guard_bash", json.dumps({"hook_event_name": "PreToolUse",
                                                          "tool_name": "Bash", "tool_input": {}}))
        self.assertEqual((code, out), (0, ""))


if __name__ == "__main__":
    unittest.main()
