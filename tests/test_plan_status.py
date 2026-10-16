"""plan_status.py: which tasks of a plan are ready, the next batch, and what is stuck or waiting."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

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


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def status(self, *args, plan_path="docs/plans/M2.md"):
        proc = subprocess.run([sys.executable, str(SCRIPT), plan_path, *args, "--json"], cwd=self.repo,
                              capture_output=True, text=True, encoding="utf-8")
        return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr


class Ready(Base):
    def test_todo_with_dependencies_done(self):
        self.write("docs/plans/M2.md", plan(
            task(1, "done (abc1234)"), task(2, depends="T1"), task(3, depends="T2"), task(4)))
        code, out, err = self.status()
        self.assertEqual(code, 0, err)
        self.assertEqual(out["ready"], ["T2", "T4"])

    def test_blocked_and_in_progress_are_not_ready(self):
        self.write("docs/plans/M2.md", plan(task(1, "blocked: review not passing"), task(2, "in-progress"), task(3)))
        code, out, _ = self.status()
        self.assertEqual(out["ready"], ["T3"])
        self.assertEqual(out["in_progress"], ["T2"])
        self.assertEqual(out["blocked"], [{"task": "T1", "reason": "review not passing"}])

    def test_a_dependency_that_is_blocked_holds_the_task(self):
        self.write("docs/plans/M2.md", plan(task(1, "blocked: no"), task(2, depends="T1")))
        self.assertEqual(self.status()[1]["ready"], [])


class Batch(Base):
    def test_first_ready_plus_its_parallel_safe_peers_at_most_three(self):
        self.write("docs/plans/M2.md", plan(
            task(1, parallel="T3, T4, T5, T6"), task(2), task(3), task(4, depends="T2"), task(5), task(6)))
        code, out, _ = self.status()
        self.assertEqual(out["batch"], ["T1", "T3", "T5"])

    def test_max(self):
        self.write("docs/plans/M2.md", plan(task(1, parallel="T2, T3"), task(2), task(3)))
        self.assertEqual(self.status("--max", "1")[1]["batch"], ["T1"])

    def test_peer_must_itself_be_ready(self):
        self.write("docs/plans/M2.md", plan(task(1, parallel="T2"), task(2, "in-progress")))
        self.assertEqual(self.status()[1]["batch"], ["T1"])

    def test_nothing_ready(self):
        self.write("docs/plans/M2.md", plan(task(1, "done (abc1234)")))
        out = self.status()[1]
        self.assertEqual((out["ready"], out["batch"], out["done"]), ([], [], ["T1"]))


class Issues(Base):
    def test_an_open_issue_holds_the_task_it_blocks(self):
        self.write("docs/plans/M2.md", plan(task(1), task(2)))
        self.write("docs/issues/0001-broken.md", ISSUE.format(status="open", blocks="docs/plans/M2.md T1"))
        out = self.status()[1]
        self.assertEqual(out["ready"], ["T2"])
        self.assertEqual(out["waiting"], [{"task": "T1", "issues": ["I-0001"]}])

    def test_a_fixed_or_wontfix_issue_does_not(self):
        self.write("docs/plans/M2.md", plan(task(1)))
        self.write("docs/issues/0001-broken.md", ISSUE.format(status="wontfix: fine", blocks="docs/plans/M2.md T1"))
        self.assertEqual(self.status()[1]["ready"], ["T1"])

    def test_issue_for_another_plan(self):
        self.write("docs/plans/M2.md", plan(task(1)))
        self.write("docs/issues/0001-broken.md", ISSUE.format(status="open", blocks="docs/plans/M3.md T1"))
        self.assertEqual(self.status()[1]["ready"], ["T1"])


class OtherTaskLetters(Base):
    def test_fix_tasks_and_suffixes_count(self):
        fix = task(2).replace("### T2", "### F1")
        later = task(3, depends="F1").replace("### T3", "### T3b")
        self.write("docs/plans/M2.md", plan(task(1, "done (abc1234)"), fix, later))
        code, out, err = self.status()
        self.assertEqual(code, 0, err)
        self.assertEqual(out["ready"], ["F1"])  # T3b waits for F1
        self.assertEqual(out["done"], ["T1"])

    def test_rule_ids_in_dependencies_are_not_tasks(self):
        self.write("docs/plans/M2.md", plan(task(1, depends="none (MATCH-010 is covered elsewhere)")))
        code, out, err = self.status()
        self.assertEqual((code, out["ready"]), (0, ["T1"]), err)


class Errors(Base):
    def test_unknown_status_and_missing_dependency(self):
        self.write("docs/plans/M2.md", plan(task(1, "finished"), task(2, depends="T9")))
        code, out, _ = self.status()
        self.assertEqual(code, 1)
        self.assertEqual(len(out["errors"]), 2)
        self.assertIn("T1", out["errors"][0])
        self.assertIn("T9", out["errors"][1])

    def test_missing_plan(self):
        code, out, err = self.status(plan_path="docs/plans/M9.md")
        self.assertEqual(code, 1)

    def test_text_output(self):
        self.write("docs/plans/M2.md", plan(task(1, parallel="T2"), task(2)))
        proc = subprocess.run([sys.executable, str(SCRIPT), "docs/plans/M2.md"], cwd=self.repo,
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("batch: T1, T2", proc.stdout)


if __name__ == "__main__":
    unittest.main()
