"""plan_status.py: which tasks of a plan are ready, the next batch, and what is stuck or waiting."""

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "implement" / "scripts" / "plan_status.py"


def task(n, status="todo", depends="none", parallel="none", title=None):
    return f"""### T{n} · {title or f"Task {n}"}
- Status: {status}
- Rules: MATCH-0{n:02d}
- App: web
- Test first: web/x{n}.test.ts — MATCH-0{n:02d}: does it
- Then implement: web/x{n}.ts
- Done when: npm test passes
- Depends on: {depends}
- Parallel-safe with: {parallel}
- Notes: none
"""


def plan(*tasks):
    return "# Plan: M2 Things\nPlanned: 2026-10-16\n\n## Tasks\n" + "\n".join(tasks) + \
           "\n## Rules covered\n- MATCH-001 → T1\n\n## Blockers\nnone\n"


ISSUE = """# I-0001 — Broken thing

- Status: {status}
- Found: reported by the developer
- Blocks: {blocks}
- Related to: none
- Rules: MATCH-001

## What happens
## What should happen
## How to see it
## Test that must fail first
`web/x.test.ts` — `MATCH-001: works`
"""


def git_init(path):
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)


def write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def status(repo, *args, plan_path="docs/plans/M2.md"):
    proc = subprocess.run([sys.executable, str(SCRIPT), plan_path, *args, "--json"], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8", check=False)
    return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr


@pytest.fixture
def repo(tmp_path):
    git_init(tmp_path)
    return tmp_path


# Ready

def test_todo_with_dependencies_done(repo):
    write(repo, "docs/plans/M2.md", plan(
        task(1, "done (abc1234)"), task(2, depends="T1"), task(3, depends="T2"), task(4)))
    code, out, err = status(repo)
    assert code == 0, err
    assert out["ready"] == ["T2", "T4"]


def test_blocked_and_in_progress_are_not_ready(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, "blocked: review not passing"), task(2, "in-progress"), task(3)))
    _, out, _ = status(repo)
    assert out["ready"] == ["T3"]
    assert out["in_progress"] == ["T2"]
    assert out["blocked"] == [{"task": "T1", "reason": "review not passing"}]


def test_a_dependency_that_is_blocked_holds_the_task(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, "blocked: no"), task(2, depends="T1")))
    assert status(repo)[1]["ready"] == []


# Batch

def test_first_ready_plus_its_parallel_safe_peers_at_most_three(repo):
    write(repo, "docs/plans/M2.md", plan(
        task(1, parallel="T3, T4, T5, T6"), task(2), task(3), task(4, depends="T2"), task(5), task(6)))
    _, out, _ = status(repo)
    assert out["batch"] == ["T1", "T3", "T5"]


def test_max(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, parallel="T2, T3"), task(2), task(3)))
    assert status(repo, "--max", "1")[1]["batch"] == ["T1"]


def test_peer_must_itself_be_ready(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, parallel="T2"), task(2, "in-progress")))
    assert status(repo)[1]["batch"] == ["T1"]


def test_nothing_ready(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, "done (abc1234)")))
    out = status(repo)[1]
    assert (out["ready"], out["batch"], out["done"]) == ([], [], ["T1"])


# Issues

def test_an_open_issue_holds_the_task_it_blocks(repo):
    write(repo, "docs/plans/M2.md", plan(task(1), task(2)))
    write(repo, "docs/issues/0001-broken.md", ISSUE.format(status="open", blocks="docs/plans/M2.md T1"))
    out = status(repo)[1]
    assert out["ready"] == ["T2"]
    assert out["waiting"] == [{"task": "T1", "issues": ["I-0001"], "blockers": []}]


def test_a_fixed_or_wontfix_issue_does_not(repo):
    write(repo, "docs/plans/M2.md", plan(task(1)))
    write(repo, "docs/issues/0001-broken.md", ISSUE.format(status="wontfix: fine", blocks="docs/plans/M2.md T1"))
    assert status(repo)[1]["ready"] == ["T1"]


def test_issue_for_another_plan(repo):
    write(repo, "docs/plans/M2.md", plan(task(1)))
    write(repo, "docs/issues/0001-broken.md", ISSUE.format(status="open", blocks="docs/plans/M3.md T1"))
    assert status(repo)[1]["ready"] == ["T1"]


# Other task letters

def test_fix_tasks_and_suffixes_count(repo):
    fix = task(2).replace("### T2", "### F1")
    later = task(3, depends="F1").replace("### T3", "### T3b")
    write(repo, "docs/plans/M2.md", plan(task(1, "done (abc1234)"), fix, later))
    code, out, err = status(repo)
    assert code == 0, err
    assert out["ready"] == ["F1"]  # T3b waits for F1
    assert out["done"] == ["T1"]


def test_rule_ids_in_dependencies_are_not_tasks(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, depends="none (MATCH-010 is covered elsewhere)")))
    code, out, err = status(repo)
    assert (code, out["ready"]) == (0, ["T1"]), err


# Plan blockers: a task may depend on an entry of the plan's Blockers (`needs the developer (B18)`)

BLOCKERS = "## Blockers\n- B18 (needs Gabriel, blocks T2 only): exports from Google Docs.\n"


def with_blockers(text):
    return text.replace("## Blockers\nnone\n", BLOCKERS)


def test_a_blocker_holds_the_task_and_is_not_an_error(repo):
    write(repo, "docs/plans/M2.md", with_blockers(
        plan(task(1, "done (abc1234)"), task(2, depends="T1; needs Gabriel (B18)"))))
    code, out, err = status(repo)
    assert (code, out["errors"]) == (0, []), err
    assert (out["ready"], out["batch"]) == ([], [])
    assert out["waiting"] == [{"task": "T2", "issues": [], "blockers": ["B18"]}]


def test_a_blocked_task_still_waits_for_its_task_dependencies_first(repo):
    write(repo, "docs/plans/M2.md", with_blockers(
        plan(task(1), task(2, depends="T1, B18"))))
    code, out, err = status(repo)
    assert (code, out["ready"], out["waiting"]) == (0, ["T1"], []), err


def test_once_the_blocker_is_gone_from_the_list_the_task_is_ready(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, "done (abc1234)"), task(2, depends="T1, B18")))
    code, out, _ = status(repo)
    assert code == 1
    assert "B18" in out["errors"][0]  # not a task and no longer a blocker: an error


def test_text_output_names_the_blocker(repo):
    write(repo, "docs/plans/M2.md", with_blockers(
        plan(task(1, "done (abc1234)"), task(2, depends="T1 (B18)"))))
    proc = subprocess.run([sys.executable, str(SCRIPT), "docs/plans/M2.md"], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8", check=False)
    assert "waiting: T2 on B18 (Blockers)" in proc.stdout


# Errors

def test_unknown_status_and_missing_dependency(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, "finished"), task(2, depends="T9")))
    code, out, _ = status(repo)
    assert code == 1
    assert len(out["errors"]) == 2
    assert "T1" in out["errors"][0]
    assert "T9" in out["errors"][1]


def test_missing_plan(repo):
    code, _, _ = status(repo, plan_path="docs/plans/M9.md")
    assert code == 1


def test_text_output(repo):
    write(repo, "docs/plans/M2.md", plan(task(1, parallel="T2"), task(2)))
    proc = subprocess.run([sys.executable, str(SCRIPT), "docs/plans/M2.md"], cwd=repo,
                          capture_output=True, text=True, check=False)
    assert proc.returncode == 0
    assert "batch: T1, T2" in proc.stdout


# Siblings: a frontend and a backend repository holding the same plan; each builds the tasks of its Repo

@pytest.fixture
def pair(tmp_path):
    """The frontend repository (where the script runs) and its backend sibling."""
    back = tmp_path / "back"
    back.mkdir()
    git_init(back)
    front = tmp_path / "front"
    front.mkdir()
    git_init(front)
    write(front, ".claude/devflow.json", json.dumps({"repo": "frontend", "siblings": {"backend": "../back"}}))
    return front, back


def write_plans(front, back, front_tasks, back_tasks):
    write(front, "docs/plans/M2.md", plan(*front_tasks))
    write(back, "docs/plans/M2.md", plan(*back_tasks))


def on(repo_name, text):
    return text.replace("- App: web", f"- Repo: {repo_name}")


def test_a_sibling_task_is_never_in_the_batch_and_its_status_comes_from_the_sibling(pair):
    front, back = pair
    write_plans(
        front, back,
        [on("backend", task(1)), on("frontend", task(2, depends="T1")), on("frontend", task(3))],
        [on("backend", task(1, "done (abc1234)")), on("frontend", task(2, depends="T1")),
         on("frontend", task(3))])
    code, out, err = status(front)
    assert code == 0, err
    assert out["ready"] == ["T2", "T3"]
    assert out["elsewhere"] == [{"task": "T1", "repo": "backend", "status": "done"}]
    assert out["done"] == []


def test_a_dependency_on_an_unfinished_sibling_task_holds_the_task(pair):
    front, back = pair
    write_plans(
        front, back,
        [on("backend", task(1, "done (abc1234)")), on("frontend", task(2, depends="T1"))],
        [on("backend", task(1, "in-progress")), on("frontend", task(2, depends="T1"))])
    out = status(front)[1]
    assert out["ready"] == []  # the local copy's stale "done" does not count
    assert out["in_progress"] == []


def test_unknown_repo(pair):
    front, back = pair
    write_plans(front, back, [on("mobile", task(1))], [on("mobile", task(1))])
    code, out, _ = status(front)
    assert code == 1
    assert "mobile" in out["errors"][0]


def test_sibling_without_the_plan(pair):
    front, _ = pair
    write(front, "docs/plans/M2.md", plan(on("backend", task(1))))
    code, out, _ = status(front)
    assert code == 1
    assert "backend: its copy of the plan" in out["errors"][0]


def test_siblings_without_repo(pair):
    front, back = pair
    write(front, ".claude/devflow.json", json.dumps({"siblings": {"backend": "../back"}}))
    write_plans(front, back, [on("backend", task(1))], [on("backend", task(1))])
    code, out, _ = status(front)
    assert code == 1
    assert "`repo`" in out["errors"][0]


# Planner choices

def test_every_planner_choice_is_listed_with_its_task(repo):
    t1 = task(1).replace("- Notes: none", "- Notes: reuse the login helper. Planner choice: the wrong "
                         "password is the real one plus `-wrong`. Planner choice: two accounts")
    write(repo, "docs/plans/M2.md", plan(t1, task(2)))
    code, out, err = status(repo)
    assert code == 0, err
    assert out["choices"] == [
        {"task": "T1", "choice": "the wrong password is the real one plus `-wrong`."},
        {"task": "T1", "choice": "two accounts"}]


def test_none(repo):
    write(repo, "docs/plans/M2.md", plan(task(1)))
    assert status(repo)[1]["choices"] == []
