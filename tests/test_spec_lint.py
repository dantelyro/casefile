"""spec_lint.py: a project's specs hold together — headings, IDs, tags, build order, links, file table."""

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "write-specs" / "scripts" / "spec_lint.py"

README = """# Specs

| File | What |
|---|---|
| [10-auth.md](10-auth.md) | Sign in |
| [12-matching.md](12-matching.md) | The score |
"""

AUTH = """# Auth

### AUTH-001 · Sign in with email
Given a user
When they sign in
Then they are in

### Notes on providers
Free text, not a rule.
"""

MATCHING = """# Matching

### MATCH-001 · Required skills weigh 70%
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

LEGEND = "✅ decided by dantelyro · ❌ rejected by dantelyro"

DECISIONS = f"""# Product decisions

{LEGEND}

- ✅ Brazil first (2026-10-01) → [AUTH-001](../specs/10-auth.md#auth-001), see D-001.
- ❌ Required skills dominate (2026-10-02) → MATCH-001.
"""


def write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def edit(repo, rel, old, new):
    p = repo / rel
    text = p.read_text(encoding="utf-8")
    assert old in text
    p.write_text(text.replace(old, new), encoding="utf-8")


def lint(repo):
    r = subprocess.run([sys.executable, str(SCRIPT), "--json"], cwd=repo, capture_output=True,
                       text=True, encoding="utf-8", check=False)
    out = json.loads(r.stdout)
    return r.returncode, out


def assert_error(repo, *parts):
    code, out = lint(repo)
    assert code == 1, out
    hits = [e for e in out["errors"] if all(p in e for p in parts)]
    assert hits, f"no error with {parts}: {out['errors']}"
    return out


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    write(tmp_path, "docs/specs/README.md", README)
    write(tmp_path, "docs/specs/10-auth.md", AUTH)
    write(tmp_path, "docs/specs/12-matching.md", MATCHING)
    write(tmp_path, "docs/product/blueprint.html", BLUEPRINT)
    write(tmp_path, "docs/product/product-decisions.md", DECISIONS)
    write(tmp_path, "docs/decisions/0001-brazil-first.md", "# D-001 — Brazil first\n\n**Status:** Accepted.\n")
    return tmp_path


# Clean

def test_a_consistent_project_passes(repo):
    code, out = lint(repo)
    assert (code, out["errors"], out["warnings"]) == (0, [], [])
    assert out["rules"] == 5


def test_text_output(repo):
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", "Sign in with email     [MUST]")
    r = subprocess.run([sys.executable, str(SCRIPT)], cwd=repo, capture_output=True, text=True,
                       encoding="utf-8", check=False)
    assert r.returncode == 1
    assert "ERROR docs/specs/10-auth.md:3" in r.stdout


# Headings

def test_a_rule_heading_without_the_separator_does_not_parse(repo):
    edit(repo, "docs/specs/10-auth.md", "AUTH-001 · Sign", "AUTH-001 Sign")
    assert_error(repo, "docs/specs/10-auth.md:3", "AUTH-001")


def test_RULE_001_a_rule_heading_without_a_tag_passes(repo):
    code, out = lint(repo)
    assert (code, out["errors"]) == (0, [])
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", "Sign in with email   ")
    assert lint(repo)[1]["errors"] == []


def test_RULE_001_later_verify_and_manual_are_allowed_alone_and_together(repo):
    for tags in ("[LATER][VERIFY]", "[MANUAL]", "[VERIFY] [MANUAL]"):
        write(repo, "docs/specs/10-auth.md", AUTH.replace("Sign in with email", f"Sign in with email     {tags}"))
        assert lint(repo)[1]["errors"] == [], tags


def test_RULE_001_mvp_is_an_error_that_says_to_remove_the_tag(repo):
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", "Sign in with email     [MVP]")
    assert_error(repo, "docs/specs/10-auth.md:3", "AUTH-001", "MVP", "remove")


def test_RULE_001_mvp_next_to_an_allowed_tag_is_still_an_error(repo):
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", "Sign in with email     [MVP][VERIFY]")
    assert_error(repo, "docs/specs/10-auth.md:3", "AUTH-001", "MVP", "remove")


def test_RULE_001_an_unknown_tag_names_the_allowed_ones(repo):
    edit(repo, "docs/specs/12-matching.md", "[LATER]", "[SOON]")
    assert_error(repo, "12-matching.md:4", "MATCH-002", "SOON", "LATER", "VERIFY", "MANUAL")


def test_RULE_001_a_heading_with_no_title_does_not_parse(repo):
    edit(repo, "docs/specs/10-auth.md", "AUTH-001 · Sign in with email", "AUTH-001 · ")
    out = assert_error(repo, "docs/specs/10-auth.md:3", "AUTH-001", "does not parse")
    hit = next(e for e in out["errors"] if "10-auth.md:3" in e)
    assert hit.endswith("`### AUTH-001 · Title`")
    assert "MVP" not in hit


@pytest.mark.parametrize("title", [
    "Sign in[MVP]",
    "[MVP]",
    "[LATER]",
    "Sign in     [mvp]",
    "Sign in [MVP] (old)",
    "[MVP] Sign in",
    "[MVP] Sign in     [LATER]",
    "[mvp] Sign in",
    "[SOON] Sign in",
    "[MANUAL] is the developer's to test",
    "Sign in [MVP ]",
    "Sign in [ MVP ]",
    "Sign in [MVP2]",
    "Sign in [MVP-1]",
    "Sign in ［MVP］",
])
def test_RULE_001_a_bracketed_word_in_a_title_does_not_parse(repo, title):
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", title)
    assert_error(repo, "docs/specs/10-auth.md:3", "AUTH-001", "does not parse")


def test_RULE_001_the_mvp_error_cites_the_decision(repo):
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", "Sign in with email     [MVP]")
    assert_error(repo, "AUTH-001", "MVP", "D-049")


def test_RULE_001_an_unknown_tag_after_an_allowed_one_is_an_error(repo):
    edit(repo, "docs/specs/10-auth.md", "Sign in with email", "Sign in with email     [VERIFY][SOON]")
    assert_error(repo, "10-auth.md:3", "AUTH-001", "SOON")


def test_an_id_used_twice_names_both_places(repo):
    write(repo, "docs/specs/README.md", README + "| [13-jobs.md](13-jobs.md) | Jobs |\n")
    write(repo, "docs/specs/13-jobs.md", "# Jobs\n\n### MATCH-002 · Again\n")
    assert_error(repo, "MATCH-002", "12-matching.md:4", "13-jobs.md:3")


def test_other_headings_and_the_readme_are_not_rules(repo):
    write(repo, "docs/specs/README.md", README + "\n### FORMAT-001 is how a heading looks\n")
    code, out = lint(repo)
    assert (code, out["errors"]) == (0, [])


# Build order

def test_a_rule_the_build_order_names_must_exist(repo):
    edit(repo, "docs/product/blueprint.html", "AUTH-001.</p>", "AUTH-001, AUTH-002.</p>")
    assert_error(repo, "build order", "AUTH-002")


def test_only_the_build_order_section_counts(repo):
    _, out = lint(repo)  # MATCH-999 and MATCH-998 sit in other sections of the same file
    assert out["errors"] == []


def test_a_markdown_build_order(repo):
    (repo / "docs/product/blueprint.html").unlink()
    write(repo, ".claude/devflow.json", json.dumps({"build_order": "docs/blueprint.md"}))
    write(repo, "docs/blueprint.md", "# Blueprint\n\nMATCH-777 elsewhere.\n\n## Build order\n\n- M1: MATCH-001, AUTH-009\n\n## Later\n\nMATCH-888\n")
    out = assert_error(repo, "build order", "AUTH-009")
    assert not [e for e in out["errors"] if "MATCH-777" in e or "MATCH-888" in e]


def test_no_build_order_yet_is_a_warning(repo):
    (repo / "docs/product/blueprint.html").unlink()
    code, out = lint(repo)
    assert (code, out["errors"]) == (0, [])
    assert any("build order" in w for w in out["warnings"])


def test_a_build_order_file_with_no_build_order_section_is_an_error(repo):
    write(repo, "docs/product/blueprint.html", "<html><body><h2>Architecture</h2></body></html>")
    assert_error(repo, "Build order")


# Product decisions

def test_a_link_to_a_missing_file(repo):
    edit(repo, "docs/product/product-decisions.md", "../specs/10-auth.md", "../specs/11-auth.md")
    assert_error(repo, "product-decisions.md", "11-auth.md")


def test_a_rule_that_does_not_exist(repo):
    edit(repo, "docs/product/product-decisions.md", "→ MATCH-001", "→ MATCH-010")
    assert_error(repo, "product-decisions.md", "MATCH-010")


def test_a_decision_entry_that_does_not_exist(repo):
    edit(repo, "docs/product/product-decisions.md", "see D-001", "see D-004")
    assert_error(repo, "product-decisions.md", "D-004")


def test_outside_links_are_not_checked(repo):
    edit(repo, "docs/product/product-decisions.md", "→ MATCH-001.", "→ MATCH-001, [Stripe](https://stripe.com/x).")
    assert lint(repo)[1]["errors"] == []


def test_no_product_decisions_file_is_fine(repo):
    (repo / "docs/product/product-decisions.md").unlink()
    assert lint(repo) == (0, {"rules": 5, "errors": [], "warnings": []})


PD = "docs/product/product-decisions.md"


def test_SPEC_008_a_file_with_the_legend_and_icons_passes(repo):
    code, out = lint(repo)
    assert (code, out["errors"]) == (0, [])


def test_SPEC_008_a_line_without_an_icon_is_an_error_naming_the_line(repo):
    edit(repo, PD, "- ❌ Required", "- Required")
    assert_error(repo, PD + ":6", "✅")


def test_SPEC_008_an_icon_without_the_space_after_it_is_an_error(repo):
    edit(repo, PD, "- ✅ Brazil first", "- ✅Brazil first")
    assert_error(repo, PD + ":5", "✅")


def test_SPEC_008_wrapped_continuation_lines_are_not_decision_lines(repo):
    edit(repo, PD, "- ✅ Brazil first", "- ✅ Brazil first\n  wrapped text with no icon")
    code, out = lint(repo)
    assert (code, out["errors"]) == (0, [])


def test_SPEC_008_a_file_without_the_legend_is_an_error(repo):
    edit(repo, PD, LEGEND + "\n\n", "")
    assert_error(repo, PD, "legend")


def test_SPEC_008_a_legend_after_a_decision_line_is_an_error(repo):
    edit(repo, PD, LEGEND + "\n\n", "- ✅ Early line\n\n" + LEGEND + "\n\n")
    assert_error(repo, PD, "legend")


@pytest.mark.parametrize("legend", [
    "✅ decided by  · ❌ rejected by dantelyro",
    "✅ decided by dantelyro · ❌ rejected by ",
    "✅ decided by dantelyro · ❌ rejected by",
])
def test_SPEC_008_a_legend_with_no_name_is_an_error(repo, legend):
    edit(repo, PD, LEGEND, legend)
    assert_error(repo, PD, "legend")


def test_SPEC_008_indented_nested_items_are_not_decision_lines(repo):
    edit(repo, PD, "- ✅ Brazil first", "- ✅ Brazil first\n  - nested item with no icon")
    code, out = lint(repo)
    assert (code, out["errors"]) == (0, [])


# File table

def test_a_spec_file_missing_from_the_table(repo):
    write(repo, "docs/specs/13-jobs.md", "# Jobs\n")
    assert_error(repo, "README.md", "13-jobs.md")


def test_a_table_row_for_a_missing_file(repo):
    (repo / "docs/specs/10-auth.md").unlink()
    edit(repo, "docs/product/product-decisions.md", "[AUTH-001](../specs/10-auth.md#auth-001)", "x")
    edit(repo, "docs/product/product-decisions.md", "→ x", "→ MATCH-001")
    edit(repo, "docs/product/blueprint.html", "AUTH-001.", ".")
    assert_error(repo, "README.md", "10-auth.md")


def test_no_readme_is_an_error(repo):
    (repo / "docs/specs/README.md").unlink()
    assert_error(repo, "README.md")


def test_no_specs_folder_is_an_error(repo):
    write(repo, ".claude/devflow.json", json.dumps({"specs_dir": "specs"}))
    assert_error(repo, "specs")
