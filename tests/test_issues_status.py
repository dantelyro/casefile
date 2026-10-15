"""issues_status.py: the mechanical half of docs/issues/ — list, check, block, number."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "fix-bug" / "scripts" / "issues_status.py"


def issue(num, title, status="open", blocks="none", test="`web/x.test.ts` — `BUG-7: upload keeps the file`"):
    return f"""# I-{num:04d} — {title}

- Status: {status}
- Found: 2026-10-14, during docs/plans/M1.md T11
- Blocks: {blocks}
- Related to: docs/plans/M1.md T8
- Rules: MATCH-013

## What happens
It breaks.

## What should happen
It works.

## How to see it
Run it.

## Test that must fail first
{test}
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
            subprocess.run(["git", *args], cwd=self.repo, check=True)
        (self.repo / "docs" / "issues").mkdir(parents=True)
        self.commit("init", allow_empty=True)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def commit(self, message, allow_empty=False):
        subprocess.run(["git", "add", "-A"], cwd=self.repo, check=True)
        args = ["git", "commit", "-q", "-m", message] + (["--allow-empty"] if allow_empty else [])
        subprocess.run(args, cwd=self.repo, check=True)
        return subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=self.repo, check=True,
                              capture_output=True, text=True).stdout.strip()

    def run_script(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args, "--json"], cwd=self.repo,
                              capture_output=True, text=True, encoding="utf-8")
        return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr


class Listing(Base):
    def test_open_and_in_progress_with_what_they_block(self):
        self.write("docs/issues/0001-a.md", issue(1, "A", blocks="docs/plans/M2.md T3"))
        self.write("docs/issues/0002-b.md", issue(2, "B", status="in-progress"))
        self.write("docs/issues/0003-c.md", issue(3, "C", status="wontfix: not worth it"))
        code, out, err = self.run_script()
        self.assertEqual(code, 0, err)
        self.assertEqual([(i["id"], i["status"], i["blocks"]) for i in out["open"]],
                         [("I-0001", "open", "docs/plans/M2.md T3"), ("I-0002", "in-progress", None)])
        self.assertEqual(out["errors"], [])

    def test_no_issues_folder(self):
        (self.repo / "docs" / "issues").rmdir()
        code, out, _ = self.run_script()
        self.assertEqual((code, out["open"], out["errors"]), (0, [], []))


class Fixed(Base):
    def test_fixed_on_the_default_branch_with_its_test(self):
        self.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
        sha = self.commit("fix")
        self.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
        code, out, err = self.run_script()
        self.assertEqual((code, out["errors"]), (0, []), err)

    def test_commit_that_does_not_exist(self):
        self.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
        self.commit("test")
        self.write("docs/issues/0001-a.md", issue(1, "A", status="fixed (deadbee)"))
        code, out, _ = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("no such commit", out["errors"][0])

    def test_commit_only_on_another_branch(self):
        subprocess.run(["git", "switch", "-q", "-c", "side"], cwd=self.repo, check=True)
        self.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
        sha = self.commit("fix on side")
        subprocess.run(["git", "switch", "-q", "main"], cwd=self.repo, check=True)
        self.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
        code, out, _ = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("that commit is not on `main`", out["errors"][0])

    def test_named_test_missing(self):
        sha = self.commit("fix without test", allow_empty=True)
        self.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
        code, out, _ = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("BUG-7: upload keeps the file", out["errors"][0])

    def test_default_branch_from_config(self):
        subprocess.run(["git", "branch", "-m", "main", "trunk"], cwd=self.repo, check=True)
        self.write(".claude/devflow.json", '{"default_branch": "trunk"}')
        self.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
        sha = self.commit("fix")
        self.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
        code, out, err = self.run_script()
        self.assertEqual((code, out["errors"]), (0, []), err)


class Malformed(Base):
    def test_bad_status_and_missing_reason(self):
        self.write("docs/issues/0001-a.md", issue(1, "A", status="done"))
        self.write("docs/issues/0002-b.md", issue(2, "B", status="wontfix"))
        code, out, _ = self.run_script()
        self.assertEqual(code, 1)
        self.assertEqual(len(out["errors"]), 2)
        self.assertIn("0001-a.md", out["errors"][0])

    def test_unparseable_file(self):
        self.write("docs/issues/0001-a.md", "just some notes\n")
        code, out, _ = self.run_script()
        self.assertEqual(code, 1)
        self.assertIn("0001-a.md", out["errors"][0])

    def test_id_must_match_file_number(self):
        self.write("docs/issues/0002-a.md", issue(1, "A"))
        code, out, _ = self.run_script()
        self.assertEqual(code, 1)


class Blocks(Base):
    def test_issues_blocking_a_task(self):
        self.write("docs/issues/0001-a.md", issue(1, "A", blocks="docs/plans/M2.md T3"))
        self.write("docs/issues/0002-b.md", issue(2, "B", blocks="docs/plans/M2.md T4"))
        self.write("docs/issues/0003-c.md", issue(3, "C", status="wontfix: no", blocks="docs/plans/M2.md T3"))
        code, out, _ = self.run_script("--blocks", "docs/plans/M2.md", "T3")
        self.assertEqual((code, out["blocking"]), (0, ["I-0001"]))
        code, out, _ = self.run_script("--blocks", "docs/plans/M2.md", "T9")
        self.assertEqual(out["blocking"], [])


class NextId(Base):
    def test_from_the_highest_file(self):
        self.write("docs/issues/0001-a.md", issue(1, "A"))
        self.write("docs/issues/0007b-b.md", issue(7, "B").replace("I-0007", "I-0007b"))
        code, out, _ = self.run_script("--next-id")
        self.assertEqual(out["next_id"], "I-0008")
        self.assertEqual(out["next_file_prefix"], "0008")

    def test_first_issue(self):
        code, out, _ = self.run_script("--next-id")
        self.assertEqual(out["next_id"], "I-0001")


class Text(Base):
    def test_plain_output_lists_and_reports(self):
        self.write("docs/issues/0001-a.md", issue(1, "A", blocks="docs/plans/M2.md T3"))
        proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo, capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0)
        self.assertIn("I-0001", proc.stdout)
        self.assertIn("blocks docs/plans/M2.md T3", proc.stdout)


if __name__ == "__main__":
    unittest.main()
