"""rules_coverage.py: which rules in a plan's scope have a test named after them."""

import json
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "plugins" / "devflow" / "skills" / "implement" / "scripts" / "rules_coverage.py"

SPEC = """# Matching

### MATCH-001 · Required skills weigh 70%
text
### MATCH-002 · Nice skills weigh 20%
### MATCH-003 · Title family
### MATCH-004 · Manual look     [MANUAL]
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


def write(repo, rel, text):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def coverage(repo, plan="docs/plans/M2.md"):
    proc = subprocess.run([sys.executable, str(SCRIPT), plan, "--json"], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8", check=False)
    return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr


@pytest.fixture
def repo(tmp_path):
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=tmp_path, check=True)
    write(tmp_path, "docs/specs/12-matching.md", SPEC)
    write(tmp_path, "docs/plans/M2.md", PLAN)
    return tmp_path


# Coverage

def test_named_tests_in_both_styles(repo):
    write(repo, "web/score.test.ts", "it('MATCH-001: required skills weigh 70%', () => {})\n"
                                     'test("MATCH-002 nice skills", () => {})\n')
    write(repo, "worker/tests/test_title.py", "def test_MATCH_003_title_family():\n    pass\n")
    code, out, err = coverage(repo)
    assert code == 0, err
    assert out["covered"] == ["MATCH-001", "MATCH-002", "MATCH-003"]
    assert (out["missing"], out["manual"], out["later"]) == ([], ["MATCH-004"], ["MATCH-005"])


def test_a_missing_mvp_rule_fails(repo):
    write(repo, "web/score.test.ts", "it('MATCH-001: x', () => {})\n")
    code, out, _ = coverage(repo)
    assert code == 1
    assert out["missing"] == ["MATCH-002", "MATCH-003"]


def test_untracked_rules_are_reported_not_failed(repo):
    for name in ("MATCH-001", "MATCH-002", "MATCH-003"):
        write(repo, f"web/{name}.test.ts", f"it('{name}: x', () => {{}})\n")
    code, out, _ = coverage(repo)
    assert code == 0
    assert out["untracked"] == [{"rule": "CV-010", "tested": False}]
    write(repo, "worker/tests/test_cv.py", "def test_CV_010_reads():\n    pass\n")
    assert coverage(repo)[1]["untracked"] == [{"rule": "CV-010", "tested": True}]


# Not a test

def test_mentions_outside_test_names_do_not_count(repo):
    write(repo, "web/score.ts", "// MATCH-001: implemented here\n")
    write(repo, "web/score.test.ts", "// it('MATCH-002: commented out', () => {})\nconst x = 'MATCH-003: just text'\n")
    write(repo, "worker/test_helpers.py", "def helper_MATCH_001():\n    pass\n")
    out = coverage(repo)[1]
    assert out["covered"] == []


def test_test_shaped_calls_outside_test_files(repo):
    write(repo, "web/test-utils.ts", "export const sample = () => it('MATCH-001: not a test file', () => {})\n")
    assert coverage(repo)[1]["covered"] == []


def test_lookalike_ids_in_the_plan_are_not_in_scope(repo):
    write(repo, "docs/plans/M2.md", "# Plan: M2\n\n## Rules covered\n- MATCH-0011 → T1\n")
    out = coverage(repo)[1]
    assert (out["missing"], out["covered"], out["untracked"]) == ([], [], [])


def test_ignored_folders_and_prefix_lookalikes(repo):
    write(repo, "web/node_modules/pkg/a.test.ts", "it('MATCH-001: x', () => {})\n")
    write(repo, ".gitignore", "web/node_modules/\n")
    write(repo, "web/a.test.ts", "it('MATCH-0011: x', () => {})\n")
    assert coverage(repo)[1]["covered"] == []


# Config

def test_specs_dir_from_config(repo):
    write(repo, "rules/12-matching.md", SPEC)
    (repo / "docs/specs/12-matching.md").unlink()
    write(repo, ".claude/devflow.json", '{"specs_dir": "rules"}')
    write(repo, "web/a.test.ts", "it('MATCH-001: x', () => {})\n")
    _, out, _ = coverage(repo)
    assert "MATCH-001" in out["covered"]
    assert out["manual"] == ["MATCH-004"]


# Errors

def test_plan_without_rules_covered(repo):
    write(repo, "docs/plans/M3.md", "# Plan: M3\n\n## Tasks\n")
    code, out, _ = coverage(repo, "docs/plans/M3.md")
    assert code == 1
    assert "Rules covered" in out["errors"][0]


# Siblings

def test_a_test_in_a_sibling_repository_covers_the_rule(repo):
    back = repo / "back"
    back.mkdir()
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=back, check=True)
    (back / "api.test.ts").write_text("it('MATCH-001: required skills weigh 70%', () => {})\n", encoding="utf-8")
    write(repo, ".claude/devflow.json", json.dumps({"repo": "frontend", "siblings": {"backend": "back"}}))
    out = coverage(repo)[1]
    assert "MATCH-001" in out["covered"]


# RULE-006: a test or a reason

def plan_with(repo, lines):
    write(repo, "docs/plans/M2.md", "# Plan: M2\n\n## Rules covered\n" + "\n".join(lines) + "\n")


def test_RULE_006_an_untagged_rule_with_a_named_test_is_covered(repo):
    plan_with(repo, ["- MATCH-001 → T1 (no test: prose)"])
    write(repo, "web/a.test.ts", "it('MATCH-001: x', () => {})\n")
    code, out, err = coverage(repo)
    assert code == 0, err
    assert (out["covered"], out["missing"], out["later"]) == (["MATCH-001"], [], [])
    assert out["reasoned"] == []


def test_RULE_006_an_untagged_rule_with_a_reason_is_reasoned(repo):
    plan_with(repo, ["- MATCH-001 → T1 (no test: agent prose, checked by hand)", "- MATCH-002 → T1"])
    code, out, _ = coverage(repo)
    assert code == 1
    assert out["reasoned"] == [{"rule": "MATCH-001", "reason": "agent prose, checked by hand"}]
    assert out["missing"] == ["MATCH-002"]


def test_RULE_006_an_untagged_rule_with_neither_is_missing_and_exits_1(repo):
    plan_with(repo, ["- MATCH-001, MATCH-002, MATCH-003 → T1"])
    code, out, _ = coverage(repo)
    assert code == 1
    assert out["missing"] == ["MATCH-001", "MATCH-002", "MATCH-003"]
    assert out["later"] == []


def test_RULE_006_later_verify_and_manual_rules_need_neither(repo):
    write(repo, "docs/specs/12-matching.md", SPEC + "### MATCH-006 · Pending fact     [VERIFY]\n")
    plan_with(repo, ["- MATCH-004, MATCH-005, MATCH-006 → T1"])
    code, out, _ = coverage(repo)
    assert code == 0
    assert out["missing"] == []
    assert out["manual"] == ["MATCH-004"]
    assert out["later"] == ["MATCH-005", "MATCH-006"]


def test_RULE_006_a_reason_covers_every_rule_on_its_line_and_no_other(repo):
    plan_with(repo, ["- MATCH-001, MATCH-002 → T1 (no test: prose)", "- MATCH-003 → T2"])
    code, out, _ = coverage(repo)
    assert code == 1
    assert out["missing"] == ["MATCH-003"]
    assert [r["rule"] for r in out["reasoned"]] == ["MATCH-001", "MATCH-002"]


def test_RULE_006_an_empty_reason_does_not_count(repo):
    plan_with(repo, ["- MATCH-001 → T1 (no test: )"])
    out = coverage(repo)[1]
    assert out["missing"] == ["MATCH-001"]
    assert out["reasoned"] == []


def test_RULE_006_a_note_that_is_not_a_no_test_reason_does_not_count(repo):
    plan_with(repo, ["- MATCH-001 → T1 (T2 removes its test)"])
    out = coverage(repo)[1]
    assert out["missing"] == ["MATCH-001"]


def test_RULE_006_a_reason_left_of_the_arrow_does_not_count(repo):
    plan_with(repo, ["- MATCH-001 (no test: x) → T1"])
    out = coverage(repo)[1]
    assert out["missing"] == ["MATCH-001"]
    assert out["reasoned"] == []


def test_RULE_006_a_reason_runs_to_the_last_parenthesis(repo):
    plan_with(repo, ["- MATCH-001 → T1 (no test: prose (agent) checked by hand)"])
    out = coverage(repo)[1]
    assert out["reasoned"] == [{"rule": "MATCH-001", "reason": "prose (agent) checked by hand"}]


def test_RULE_006_a_rule_on_several_lines_is_reasoned_if_any_line_has_a_reason(repo):
    plan_with(repo, ["- MATCH-001 → T1", "- MATCH-001 → T2 (no test: prose)"])
    out = coverage(repo)[1]
    assert out["reasoned"] == [{"rule": "MATCH-001", "reason": "prose"}]
    assert out["missing"] == []


def test_RULE_006_manual_combined_with_another_tag_is_manual(repo):
    write(repo, "docs/specs/12-matching.md", SPEC + "### MATCH-006 · Both     [VERIFY] [MANUAL]\n")
    plan_with(repo, ["- MATCH-006 → T1"])
    code, out, _ = coverage(repo)
    assert code == 0
    assert (out["manual"], out["later"]) == (["MATCH-006"], [])


def test_RULE_006_the_text_output_names_reasons_and_the_manual_label(repo):
    plan_with(repo, ["- MATCH-001 → T1 (no test: prose)", "- MATCH-004 → T1"])
    proc = subprocess.run([sys.executable, str(SCRIPT), "docs/plans/M2.md"], cwd=repo,
                          capture_output=True, text=True, encoding="utf-8", check=False)
    assert "no test, with reason (1): MATCH-001 (prose)" in proc.stdout
    assert "the developer tests by hand: MATCH-004" in proc.stdout


def test_RULE_006_a_rule_still_tagged_mvp_is_checked_like_an_untagged_one(repo):
    write(repo, "docs/specs/12-matching.md", SPEC.replace("weigh 70%\n", "weigh 70%     [MVP]\n"))
    plan_with(repo, ["- MATCH-001 → T1"])
    code, out, _ = coverage(repo)
    assert code == 1
    assert out["missing"] == ["MATCH-001"]


# RULE-008: an eval named after a rule is its test

def git_init(path):
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main"], cwd=path, check=True)


def test_RULE_008_an_eval_named_after_a_rule_covers_it(repo):
    write(repo, "evals/MATCH-001-weights/case.yaml", "name: x\n")
    _, out, err = coverage(repo)
    assert out["covered"] == ["MATCH-001"], err
    assert "MATCH-001" not in out["missing"]


def test_RULE_008_an_eval_and_a_test_together_cover_it_once(repo):
    write(repo, "evals/MATCH-001-weights/case.yaml", "name: x\n")
    write(repo, "evals/MATCH-001-other/prompt.md", "x\n")
    write(repo, "web/a.test.ts", "it('MATCH-001: x', () => {})\n")
    out = coverage(repo)[1]
    assert out["covered"] == ["MATCH-001"]


def test_RULE_008_an_eval_folder_without_a_slug_does_not_count(repo):
    write(repo, "evals/MATCH-001/case.yaml", "name: x\n")
    write(repo, "evals/MATCH-002-/case.yaml", "name: x\n")
    out = coverage(repo)[1]
    assert out["covered"] == []


def test_RULE_008_an_eval_for_another_rule_does_not_count(repo):
    write(repo, "evals/MATCH-0011-x/case.yaml", "name: x\n")
    write(repo, "evals/MATCH-002-x/case.yaml", "name: x\n")
    out = coverage(repo)[1]
    assert out["covered"] == ["MATCH-002"]


def test_RULE_008_a_folder_outside_evals_or_nested_deeper_does_not_count(repo):
    write(repo, "evals/sub/MATCH-001-x/case.yaml", "name: x\n")
    write(repo, "docs/MATCH-002-x/case.yaml", "name: x\n")
    write(repo, "plugins/devflow/evals/sub/MATCH-003-x/case.yaml", "name: x\n")
    out = coverage(repo)[1]
    assert out["covered"] == []


def test_RULE_008_an_eval_in_an_evals_folder_inside_a_plugin_counts(repo):
    write(repo, "plugins/devflow/evals/MATCH-001-x/case.yaml", "name: x\n")
    out = coverage(repo)[1]
    assert out["covered"] == ["MATCH-001"]


def test_RULE_008_an_eval_in_a_sibling_repository_counts(repo):
    git_init(repo / "back")
    write(repo, "back/evals/MATCH-003-x/prompt.md", "x\n")
    write(repo, ".claude/devflow.json", json.dumps({"repo": "frontend", "siblings": {"backend": "back"}}))
    out = coverage(repo)[1]
    assert out["covered"] == ["MATCH-003"]


def test_RULE_008_a_manual_rule_with_an_eval_stays_manual(repo):
    write(repo, "evals/MATCH-004-look/case.yaml", "name: x\n")
    out = coverage(repo)[1]
    assert out["manual"] == ["MATCH-004"]
    assert "MATCH-004" not in out["covered"]
