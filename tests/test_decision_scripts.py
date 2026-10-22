"""The decision log's mechanical parts: the next id, a new entry, the generated index."""

import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "plugins" / "devflow" / "skills" / "evidence-based-decisions" / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8", check=False)


def entry(num, title, status="Accepted (2026-10-14)."):
    return f"# D-{num:03d} — {title}\n\n**Status:** {status}\n**Decided by:** someone\n\n**Context:** Why.\n"


class Log:
    def __init__(self, repo):
        self.repo = repo
        self.log = repo / "docs" / "decisions"

    def write(self, name, text):
        self.log.mkdir(parents=True, exist_ok=True)
        (self.log / name).write_text(text, encoding="utf-8")


@pytest.fixture
def log(tmp_path):
    return Log(tmp_path)


# next id

def next_id(log):
    r = run("decision_next_id.py", cwd=log.repo)
    assert r.returncode == 0, r.stderr
    return r.stdout.strip()


def test_next_id_a_missing_or_empty_log_starts_at_one(log):
    assert next_id(log) == "D-001"
    log.log.mkdir(parents=True)
    assert next_id(log) == "D-001"


def test_next_id_one_past_the_highest_filename(log):
    log.write("0001-a.md", entry(1, "A"))
    log.write("0009-b.md", entry(9, "B"))
    log.write("0004-c.md", entry(4, "C"))
    assert next_id(log) == "D-010"


def test_next_id_letter_suffixes_and_other_files_never_raise_it(log):
    log.write("0003-a.md", entry(3, "A"))
    log.write("0003b-between.md", entry(3, "Between"))
    log.write("README.md", "# Decision log\n")
    log.write("notes.txt", "0099\n")
    assert next_id(log) == "D-004"


def test_next_id_a_folder_given_as_argument(log):
    other = log.repo / "elsewhere"
    other.mkdir()
    (other / "0041-x.md").write_text(entry(41, "X"), encoding="utf-8")
    r = run("decision_next_id.py", "elsewhere", cwd=log.repo)
    assert r.stdout.strip() == "D-042"


# new entry

FIELDS = ["--context", "M1 showed it.", "--options", "(a) one; (b) two.", "--decision", "(b), because.",
          "--trade-offs", "Slower.", "--decided-by", "dantelyro — Grade 1: asked in session.",
          "--date", "2026-10-16"]


def new(log, title, *extra):
    return run("decision_new.py", "--title", title, *FIELDS, *extra, cwd=log.repo)


def test_new_writes_the_next_entry_proposed_in_the_logs_format(log):
    log.write("0006-old.md", entry(6, "Old"))
    r = new(log, "Saved jobs live in their own table, not a flag on jobs")
    assert r.returncode == 0, r.stderr
    path = log.log / "0007-saved-jobs-live-in-their-own-table-not.md"
    assert r.stdout.strip() == str(path.relative_to(log.repo)).replace("\\", "/")
    assert path.read_text(encoding="utf-8") == (
        "# D-007 — Saved jobs live in their own table, not a flag on jobs\n\n"
        "**Status:** Proposed (2026-10-16).\n"
        "**Decided by:** dantelyro — Grade 1: asked in session.\n\n"
        "**Context:** M1 showed it.\n\n"
        "**Options:** (a) one; (b) two.\n\n"
        "**Decision:** (b), because.\n\n"
        "**Trade-offs:** Slower.\n")


def test_new_the_slug_drops_punctuation_and_code_marks(log):
    r = new(log, "`implement` never writes code, tests or specs; the plan is the record")
    assert r.returncode == 0, r.stderr
    assert (log.log / "0001-implement-never-writes-code-tests-or-specs-the.md").exists()


def test_new_an_apostrophe_does_not_split_a_word(log):
    r = new(log, "The log’s index and the developer's yes")
    assert r.returncode == 0, r.stderr
    assert (log.log / "0001-the-logs-index-and-the-developers-yes.md").exists()


def test_new_creates_the_folder(log):
    r = new(log, "First")
    assert r.returncode == 0, r.stderr
    assert (log.log / "0001-first.md").exists()


def test_new_every_field_is_required(log):
    r = run("decision_new.py", "--title", "T", "--context", "c", cwd=log.repo)
    assert r.returncode != 0
    assert not log.log.exists()


# index

TABLE = "| Id | Title | Status |\n| --- | --- | --- |\n"
ROWS = ("| [D-001](0001-first.md) | First | Accepted |\n"
        "| [D-002](0002-second.md) | Second | SUPERSEDED by D-003 |\n"
        "| [D-002b](0002b-between.md) | Between | Open |\n"
        "| [D-003](0003-third.md) | Third, with a comma | Proposed |\n")


def index(log, *args):
    return run("decision_index.py", *args, cwd=log.repo)


@pytest.fixture
def entries(log):
    log.write("0001-first.md", entry(1, "First"))
    log.write("0002-second.md", entry(2, "Second", "**SUPERSEDED by D-003 (2026-10-15).** It was wrong."))
    log.write("0002b-between.md", entry(2, "Between", "Open."))
    log.write("0003-third.md", entry(3, "Third, with a comma", "Proposed (2026-10-16)."))
    return log


def test_index_rebuilds_the_table_and_keeps_the_text_around_it(entries):
    entries.write("README.md", "# Decision log\n\nIntro.\n\n" + TABLE
                  + "| [D-001](x.md) | Stale | Open |\n\n## Conventions\n\nKeep.\n")
    r = index(entries)
    assert r.returncode == 0, r.stderr
    assert (entries.log / "README.md").read_text(encoding="utf-8") == (
        "# Decision log\n\nIntro.\n\n" + TABLE + ROWS + "\n## Conventions\n\nKeep.\n")


def test_index_a_log_without_a_readme_gets_one(entries):
    assert index(entries).returncode == 0
    text = (entries.log / "README.md").read_text(encoding="utf-8")
    assert text.startswith("# Decision log\n")
    assert TABLE + ROWS in text


def test_index_check_reports_a_stale_index_and_writes_nothing(entries):
    stale = "# Decision log\n\n" + TABLE + "| [D-001](0001-first.md) | First | Accepted |\n"
    entries.write("README.md", stale)
    r = index(entries, "--check")
    assert r.returncode == 1
    assert (entries.log / "README.md").read_text(encoding="utf-8") == stale
    assert index(entries).returncode == 0
    assert index(entries, "--check").returncode == 0


def test_index_keeps_crlf_line_endings(entries):
    (entries.log / "README.md").write_bytes(("# Decision log\r\n\r\n" + TABLE.replace("\n", "\r\n")).encode())
    assert index(entries).returncode == 0
    raw = (entries.log / "README.md").read_bytes()
    assert b"\n" not in raw.replace(b"\r\n", b"")
    assert b"| [D-003](0003-third.md) | Third, with a comma | Proposed |\r\n" in raw


def test_index_what_an_entry_supersedes_is_carried_into_its_status(log):
    log.write("0005-new.md", entry(5, "New", "Accepted (2026-10-15). Supersedes **D-001**, D-002b.\n"))
    assert index(log).returncode == 0
    assert ("| [D-005](0005-new.md) | New | Accepted, supersedes D-001, D-002b |\n"
            in (log.log / "README.md").read_text(encoding="utf-8"))


def test_index_an_entry_without_a_title_line_is_an_error(log):
    log.write("0001-first.md", "no heading\n")
    r = index(log)
    assert r.returncode == 1
    assert "0001-first.md" in r.stdout + r.stderr


def test_devflows_own_log_the_generated_index_is_the_committed_one():
    r = run("decision_index.py", "--check", cwd=ROOT)
    assert r.returncode == 0, r.stdout + r.stderr
