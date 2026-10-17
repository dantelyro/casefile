"""spec_lint.py: a project's specs hold together — headings, IDs, tags, build order, links, file table."""

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "write-specs" / "scripts" / "spec_lint.py"

README = """# Specs

| File | What |
|---|---|
| [10-auth.md](10-auth.md) | Sign in |
| [12-matching.md](12-matching.md) | The score |
"""

AUTH = """# Auth

### AUTH-001 · Sign in with email     [MVP]
Given a user
When they sign in
Then they are in

### Notes on providers
Free text, not a rule.
"""

MATCHING = """# Matching

### MATCH-001 · Required skills weigh 70%     [MVP]
### MATCH-002 · A score is cached     [LATER]
### MATCH-003 · Scores for 1000 jobs in 200ms     [VERIFY]
### MATCH-004 · The score reads well     [MANUAL]
"""

BLUEPRINT = """<html><body>
<nav><a href="#order">Build order</a></nav>
<section id="architecture"><p>Web calls MATCH-999 nowhere; this section is not the build order.</p></section>
<section id="order">
  <span class="eyebrow">Build order</span>
  <div class="ms"><span class="n">M1</span><h3>Matching</h3><p>MATCH-001, MATCH-002.</p></div>
  <div class="ms"><span class="n">M2</span><h3>Auth</h3><p>AUTH-001.</p></div>
</section>
<section id="later"><p>MATCH-998 is planned after the build order.</p></section>
</body></html>
"""

DECISIONS = """# Product decisions

- Brazil first (2026-10-01) → [AUTH-001](../specs/10-auth.md#auth-001), see D-001.
- Required skills dominate (2026-10-02) → MATCH-001.
"""


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.repo, check=True)
        self.write("docs/specs/README.md", README)
        self.write("docs/specs/10-auth.md", AUTH)
        self.write("docs/specs/12-matching.md", MATCHING)
        self.write("docs/product/blueprint.html", BLUEPRINT)
        self.write("docs/product/product-decisions.md", DECISIONS)
        self.write("docs/decisions/0001-brazil-first.md", "# D-001 — Brazil first\n\n**Status:** Accepted.\n")

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def edit(self, rel, old, new):
        p = self.repo / rel
        text = p.read_text(encoding="utf-8")
        self.assertIn(old, text)
        p.write_text(text.replace(old, new), encoding="utf-8")

    def lint(self):
        r = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=self.repo, capture_output=True,
                           text=True, encoding="utf-8")
        out = json.loads(r.stdout)
        return r.returncode, out

    def assertError(self, *parts):
        code, out = self.lint()
        self.assertEqual(code, 1, out)
        hits = [e for e in out["errors"] if all(p in e for p in parts)]
        self.assertTrue(hits, f"no error with {parts}: {out['errors']}")
        return out


class Clean(Base):
    def test_a_consistent_project_passes(self):
        code, out = self.lint()
        self.assertEqual((code, out["errors"], out["warnings"]), (0, [], []))
        self.assertEqual(out["rules"], 5)

    def test_text_output(self):
        self.edit("docs/specs/10-auth.md", "[MVP]", "[MUST]")
        r = subprocess.run([sys.executable, str(SCRIPT)], cwd=self.repo, capture_output=True, text=True,
                           encoding="utf-8")
        self.assertEqual(r.returncode, 1)
        self.assertIn("ERROR docs/specs/10-auth.md:3", r.stdout)


class Headings(Base):
    def test_a_rule_heading_without_the_separator_does_not_parse(self):
        self.edit("docs/specs/10-auth.md", "AUTH-001 · Sign", "AUTH-001 Sign")
        self.assertError("docs/specs/10-auth.md:3", "AUTH-001")

    def test_a_rule_heading_without_a_tag_does_not_parse(self):
        self.edit("docs/specs/10-auth.md", "Sign in with email     [MVP]", "Sign in with email")
        self.assertError("docs/specs/10-auth.md:3")

    def test_a_rule_may_carry_more_than_one_tag(self):
        self.edit("docs/specs/10-auth.md", "[MVP]", "[MVP][VERIFY]")
        self.assertEqual(self.lint()[1]["errors"], [])
        self.edit("docs/specs/10-auth.md", "[MVP][VERIFY]", "[MVP] [SOON]")
        self.assertError("10-auth.md:3", "SOON")

    def test_an_unknown_tag_is_an_error(self):
        self.edit("docs/specs/12-matching.md", "[LATER]", "[SOON]")
        self.assertError("12-matching.md:4", "SOON")

    def test_an_id_used_twice_names_both_places(self):
        self.write("docs/specs/README.md", README + "| [13-jobs.md](13-jobs.md) | Jobs |\n")
        self.write("docs/specs/13-jobs.md", "# Jobs\n\n### MATCH-002 · Again     [MVP]\n")
        self.assertError("MATCH-002", "12-matching.md:4", "13-jobs.md:3")

    def test_other_headings_and_the_readme_are_not_rules(self):
        self.write("docs/specs/README.md", README + "\n### FORMAT-001 is how a heading looks\n")
        code, out = self.lint()
        self.assertEqual((code, out["errors"]), (0, []))


class BuildOrder(Base):
    def test_a_rule_the_build_order_names_must_exist(self):
        self.edit("docs/product/blueprint.html", "AUTH-001.</p>", "AUTH-001, AUTH-002.</p>")
        self.assertError("build order", "AUTH-002")

    def test_only_the_build_order_section_counts(self):
        code, out = self.lint()  # MATCH-999 and MATCH-998 sit in other sections of the same file
        self.assertEqual(out["errors"], [])

    def test_a_markdown_build_order(self):
        (self.repo / "docs/product/blueprint.html").unlink()
        self.write(".claude/devflow.json", json.dumps({"build_order": "docs/blueprint.md"}))
        self.write("docs/blueprint.md", "# Blueprint\n\nMATCH-777 elsewhere.\n\n## Build order\n\n- M1: MATCH-001, AUTH-009\n\n## Later\n\nMATCH-888\n")
        out = self.assertError("build order", "AUTH-009")
        self.assertFalse([e for e in out["errors"] if "MATCH-777" in e or "MATCH-888" in e])

    def test_no_build_order_yet_is_a_warning(self):
        (self.repo / "docs/product/blueprint.html").unlink()
        code, out = self.lint()
        self.assertEqual((code, out["errors"]), (0, []))
        self.assertTrue(any("build order" in w for w in out["warnings"]))

    def test_a_build_order_file_with_no_build_order_section_is_an_error(self):
        self.write("docs/product/blueprint.html", "<html><body><h2>Architecture</h2></body></html>")
        self.assertError("Build order")


class ProductDecisions(Base):
    def test_a_link_to_a_missing_file(self):
        self.edit("docs/product/product-decisions.md", "../specs/10-auth.md", "../specs/11-auth.md")
        self.assertError("product-decisions.md", "11-auth.md")

    def test_a_rule_that_does_not_exist(self):
        self.edit("docs/product/product-decisions.md", "→ MATCH-001", "→ MATCH-010")
        self.assertError("product-decisions.md", "MATCH-010")

    def test_a_decision_entry_that_does_not_exist(self):
        self.edit("docs/product/product-decisions.md", "see D-001", "see D-004")
        self.assertError("product-decisions.md", "D-004")

    def test_outside_links_are_not_checked(self):
        self.edit("docs/product/product-decisions.md", "→ MATCH-001.", "→ MATCH-001, [Stripe](https://stripe.com/x).")
        self.assertEqual(self.lint()[1]["errors"], [])

    def test_no_product_decisions_file_is_fine(self):
        (self.repo / "docs/product/product-decisions.md").unlink()
        self.assertEqual(self.lint(), (0, {"rules": 5, "errors": [], "warnings": []}))


class FileTable(Base):
    def test_a_spec_file_missing_from_the_table(self):
        self.write("docs/specs/13-jobs.md", "# Jobs\n")
        self.assertError("README.md", "13-jobs.md")

    def test_a_table_row_for_a_missing_file(self):
        (self.repo / "docs/specs/10-auth.md").unlink()
        self.edit("docs/product/product-decisions.md", "[AUTH-001](../specs/10-auth.md#auth-001)", "x")
        self.edit("docs/product/product-decisions.md", "→ x", "→ MATCH-001")
        self.edit("docs/product/blueprint.html", "AUTH-001.", ".")
        self.assertError("README.md", "10-auth.md")

    def test_no_readme_is_an_error(self):
        (self.repo / "docs/specs/README.md").unlink()
        self.assertError("README.md")

    def test_no_specs_folder_is_an_error(self):
        self.write(".claude/devflow.json", json.dumps({"specs_dir": "specs"}))
        self.assertError("specs")


if __name__ == "__main__":
    unittest.main()
