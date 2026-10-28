"""issues_status.py: the mechanical half of docs/issues/ — list, check, block, number."""

import json
import pathlib
import subprocess
import sys

import pytest

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


class Repo:
    def __init__(self, path):
        self.repo = path

    def git(self, *args):
        return subprocess.run(["git", *args], cwd=self.repo, check=True, capture_output=True, text=True)

    def write(self, rel, text):
        p = self.repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def commit(self, message, allow_empty=False):
        self.git("add", "-A")
        self.git("commit", "-q", "-m", message, *(["--allow-empty"] if allow_empty else []))
        return self.git("rev-parse", "--short", "HEAD").stdout.strip()

    def run_script(self, *args):
        proc = subprocess.run([sys.executable, str(SCRIPT), *args, "--json"], cwd=self.repo,
                              capture_output=True, text=True, encoding="utf-8", check=False)
        return proc.returncode, (json.loads(proc.stdout) if proc.stdout.strip() else None), proc.stderr


@pytest.fixture
def repo(tmp_path):
    r = Repo(tmp_path)
    for args in (["init", "-q", "-b", "main"], ["config", "user.email", "t@t"], ["config", "user.name", "t"]):
        r.git(*args)
    (tmp_path / "docs" / "issues").mkdir(parents=True)
    r.commit("init", allow_empty=True)
    return r


# listing

def test_listing_open_and_in_progress_with_what_they_block(repo):
    repo.write("docs/issues/0001-a.md", issue(1, "A", blocks="docs/plans/M2.md T3"))
    repo.write("docs/issues/0002-b.md", issue(2, "B", status="in-progress"))
    repo.write("docs/issues/0003-c.md", issue(3, "C", status="wontfix: not worth it"))
    code, out, err = repo.run_script()
    assert code == 0, err
    assert [(i["id"], i["status"], i["blocks"]) for i in out["open"]] == [
        ("I-0001", "open", "docs/plans/M2.md T3"), ("I-0002", "in-progress", None)]
    assert out["errors"] == []


def test_listing_no_issues_folder(repo):
    (repo.repo / "docs" / "issues").rmdir()
    code, out, _ = repo.run_script()
    assert (code, out["open"], out["errors"]) == (0, [], [])


# fixed

def test_fixed_on_the_default_branch_with_its_test(repo):
    repo.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
    sha = repo.commit("fix")
    repo.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
    code, out, err = repo.run_script()
    assert (code, out["errors"]) == (0, []), err


def test_fixed_commit_that_does_not_exist(repo):
    repo.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
    repo.commit("test")
    repo.write("docs/issues/0001-a.md", issue(1, "A", status="fixed (deadbee)"))
    code, out, _ = repo.run_script()
    assert code == 1
    assert "no such commit" in out["errors"][0]


def test_fixed_commit_only_on_another_branch(repo):
    repo.git("switch", "-q", "-c", "side")
    repo.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
    sha = repo.commit("fix on side")
    repo.git("switch", "-q", "main")
    repo.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
    code, out, _ = repo.run_script()
    assert code == 1
    assert "that commit is not on `main`" in out["errors"][0]


def test_fixed_named_test_missing(repo):
    sha = repo.commit("fix without test", allow_empty=True)
    repo.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
    code, out, _ = repo.run_script()
    assert code == 1
    assert "BUG-7: upload keeps the file" in out["errors"][0]


def test_fixed_default_branch_from_config(repo):
    repo.git("branch", "-m", "main", "trunk")
    repo.write(".claude/casefile.json", '{"default_branch": "trunk"}')
    repo.write("web/x.test.ts", "it('BUG-7: upload keeps the file', () => {})\n")
    sha = repo.commit("fix")
    repo.write("docs/issues/0001-a.md", issue(1, "A", status=f"fixed ({sha})"))
    code, out, err = repo.run_script()
    assert (code, out["errors"]) == (0, []), err


# malformed

def test_malformed_bad_status_and_missing_reason(repo):
    repo.write("docs/issues/0001-a.md", issue(1, "A", status="done"))
    repo.write("docs/issues/0002-b.md", issue(2, "B", status="wontfix"))
    code, out, _ = repo.run_script()
    assert code == 1
    assert len(out["errors"]) == 2
    assert "0001-a.md" in out["errors"][0]


def test_malformed_unparseable_file(repo):
    repo.write("docs/issues/0001-a.md", "just some notes\n")
    code, out, _ = repo.run_script()
    assert code == 1
    assert "0001-a.md" in out["errors"][0]


def test_malformed_id_must_match_file_number(repo):
    repo.write("docs/issues/0002-a.md", issue(1, "A"))
    code, _, _ = repo.run_script()
    assert code == 1


# blocks

def test_blocks_issues_blocking_a_task(repo):
    repo.write("docs/issues/0001-a.md", issue(1, "A", blocks="docs/plans/M2.md T3"))
    repo.write("docs/issues/0002-b.md", issue(2, "B", blocks="docs/plans/M2.md T4"))
    repo.write("docs/issues/0003-c.md", issue(3, "C", status="wontfix: no", blocks="docs/plans/M2.md T3"))
    code, out, _ = repo.run_script("--blocks", "docs/plans/M2.md", "T3")
    assert (code, out["blocking"]) == (0, ["I-0001"])
    _, out, _ = repo.run_script("--blocks", "docs/plans/M2.md", "T9")
    assert out["blocking"] == []


# next id

def test_next_id_from_the_highest_file(repo):
    repo.write("docs/issues/0001-a.md", issue(1, "A"))
    repo.write("docs/issues/0007b-b.md", issue(7, "B").replace("I-0007", "I-0007b"))
    _, out, _ = repo.run_script("--next-id")
    assert out["next_id"] == "I-0008"
    assert out["next_file_prefix"] == "0008"


def test_next_id_first_issue(repo):
    _, out, _ = repo.run_script("--next-id")
    assert out["next_id"] == "I-0001"


# text

def test_text_plain_output_lists_and_reports(repo):
    repo.write("docs/issues/0001-a.md", issue(1, "A", blocks="docs/plans/M2.md T3"))
    proc = subprocess.run([sys.executable, str(SCRIPT)], cwd=repo.repo, capture_output=True, text=True,
                          check=False)
    assert proc.returncode == 0
    assert "I-0001" in proc.stdout
    assert "blocks docs/plans/M2.md T3" in proc.stdout
