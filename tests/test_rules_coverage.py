"""rules_coverage.py: which rules in a plan's scope have a test named after them."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "implement" / "scripts" / "rules_coverage.py"

SPEC = """# Matching

### MATCH-001 · Required skills weigh 70%     [MVP]
text
### MATCH-002 · Nice skills weigh 20%     [MVP]
### MATCH-003 · Title family     [MVP]
### MATCH-004 · Manual look     [MVP] [MANUAL]
### MATCH-005 · Later thing     [LATER]

| CV-010 | a table rule |
"""

PLAN = """# Plan: M2 Matching

## Tasks
### T1 · x
- Status: todo

## Rules covered
- MATCH-001 → T1
- MATCH-002, MATCH-003 → T1
- MATCH-004 → review
- MATCH-005 → later
- CV-010 → T1

## Blockers
none
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)
        self.write("docs/specs/12-matching.md", SPEC)
        self.write("docs/plans/M2.md", PLAN)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def coverage(self, plan="docs/plans/M2.md"):
        proc = subprocess.run([sys.executable, str(SCRIPT), plan, "--json"], cwd=self.repo,
                              capture_output=True, text=True, encoding="utf-8")
        return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr


class Coverage(Base):
    def test_named_tests_in_both_styles(self):
        self.write("web/score.test.ts", "it('MATCH-001: required skills weigh 70%', () => {})\n"
                                        'test("MATCH-002 nice skills", () => {})\n')
        self.write("worker/tests/test_title.py", "def test_MATCH_003_title_family():\n    pass\n")
        code, out, err = self.coverage()
        self.assertEqual(code, 0, err)
        self.assertEqual(out["covered"], ["MATCH-001", "MATCH-002", "MATCH-003"])
        self.assertEqual((out["missing"], out["manual"], out["later"]), ([], ["MATCH-004"], ["MATCH-005"]))

    def test_a_missing_mvp_rule_fails(self):
        self.write("web/score.test.ts", "it('MATCH-001: x', () => {})\n")
        code, out, _ = self.coverage()
        self.assertEqual(code, 1)
        self.assertEqual(out["missing"], ["MATCH-002", "MATCH-003"])

    def test_untracked_rules_are_reported_not_failed(self):
        for name in ("MATCH-001", "MATCH-002", "MATCH-003"):
            self.write(f"web/{name}.test.ts", f"it('{name}: x', () => {{}})\n")
        code, out, _ = self.coverage()
        self.assertEqual(code, 0)
        self.assertEqual(out["untracked"], [{"rule": "CV-010", "tested": False}])
        self.write("worker/tests/test_cv.py", "def test_CV_010_reads():\n    pass\n")
        self.assertEqual(self.coverage()[1]["untracked"], [{"rule": "CV-010", "tested": True}])


class NotATest(Base):
    def test_mentions_outside_test_names_do_not_count(self):
        self.write("web/score.ts", "// MATCH-001: implemented here\n")
        self.write("web/score.test.ts", "// it('MATCH-002: commented out', () => {})\nconst x = 'MATCH-003: just text'\n")
        self.write("worker/test_helpers.py", "def helper_MATCH_001():\n    pass\n")
        out = self.coverage()[1]
        self.assertEqual(out["covered"], [])

    def test_test_shaped_calls_outside_test_files(self):
        self.write("web/test-utils.ts", "export const sample = () => it('MATCH-001: not a test file', () => {})\n")
        self.assertEqual(self.coverage()[1]["covered"], [])

    def test_lookalike_ids_in_the_plan_are_not_in_scope(self):
        self.write("docs/plans/M2.md", "# Plan: M2\n\n## Rules covered\n- MATCH-0011 → T1\n")
        out = self.coverage()[1]
        self.assertEqual((out["missing"], out["covered"], out["untracked"]), ([], [], []))

    def test_ignored_folders_and_prefix_lookalikes(self):
        self.write("web/node_modules/pkg/a.test.ts", "it('MATCH-001: x', () => {})\n")
        self.write(".gitignore", "web/node_modules/\n")
        self.write("web/a.test.ts", "it('MATCH-0011: x', () => {})\n")
        self.assertEqual(self.coverage()[1]["covered"], [])


class Config(Base):
    def test_specs_dir_from_config(self):
        (self.repo / "docs/specs/12-matching.md").rename(self.repo / "docs/plans/../spec-elsewhere.md") \
            if False else None
        self.write("rules/12-matching.md", SPEC)
        (self.repo / "docs/specs/12-matching.md").unlink()
        self.write(".claude/devflow.json", '{"specs_dir": "rules"}')
        self.write("web/a.test.ts", "it('MATCH-001: x', () => {})\n")
        code, out, _ = self.coverage()
        self.assertIn("MATCH-001", out["covered"])
        self.assertEqual(out["manual"], ["MATCH-004"])


class Errors(Base):
    def test_plan_without_rules_covered(self):
        self.write("docs/plans/M3.md", "# Plan: M3\n\n## Tasks\n")
        code, out, _ = self.coverage("docs/plans/M3.md")
        self.assertEqual(code, 1)
        self.assertIn("Rules covered", out["errors"][0])


if __name__ == "__main__":
    unittest.main()
