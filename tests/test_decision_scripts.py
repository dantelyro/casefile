"""The decision log's mechanical parts: the next id, a new entry, the generated index."""

import pathlib
import subprocess
import sys
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "skills" / "evidence-based-decisions" / "scripts"


def run(script, *args, cwd):
    return subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")


def entry(num, title, status="Accepted (2026-10-14)."):
    return f"# D-{num:03d} — {title}\n\n**Status:** {status}\n**Decided by:** someone\n\n**Context:** Why.\n"


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = pathlib.Path(self.tmp.name)
        self.log = self.repo / "docs" / "decisions"

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text):
        self.log.mkdir(parents=True, exist_ok=True)
        (self.log / name).write_text(text, encoding="utf-8")


class NextId(Base):
    def next_id(self):
        r = run("decision_next_id.py", cwd=self.repo)
        self.assertEqual(r.returncode, 0, r.stderr)
        return r.stdout.strip()

    def test_a_missing_or_empty_log_starts_at_one(self):
        self.assertEqual(self.next_id(), "D-001")
        self.log.mkdir(parents=True)
        self.assertEqual(self.next_id(), "D-001")

    def test_one_past_the_highest_filename(self):
        self.write("0001-a.md", entry(1, "A"))
        self.write("0009-b.md", entry(9, "B"))
        self.write("0004-c.md", entry(4, "C"))
        self.assertEqual(self.next_id(), "D-010")

    def test_letter_suffixes_and_other_files_never_raise_it(self):
        self.write("0003-a.md", entry(3, "A"))
        self.write("0003b-between.md", entry(3, "Between"))
        self.write("README.md", "# Decision log\n")
        self.write("notes.txt", "0099\n")
        self.assertEqual(self.next_id(), "D-004")

    def test_a_folder_given_as_argument(self):
        other = self.repo / "elsewhere"
        other.mkdir()
        (other / "0041-x.md").write_text(entry(41, "X"), encoding="utf-8")
        r = run("decision_next_id.py", "elsewhere", cwd=self.repo)
        self.assertEqual(r.stdout.strip(), "D-042")


class NewEntry(Base):
    FIELDS = ["--context", "M1 showed it.", "--options", "(a) one; (b) two.", "--decision", "(b), because.",
              "--trade-offs", "Slower.", "--decided-by", "dantelyro — Grade 1: asked in session.",
              "--date", "2026-10-16"]

    def new(self, title, *extra):
        return run("decision_new.py", "--title", title, *self.FIELDS, *extra, cwd=self.repo)

    def test_writes_the_next_entry_proposed_in_the_logs_format(self):
        self.write("0006-old.md", entry(6, "Old"))
        r = self.new("Saved jobs live in their own table, not a flag on jobs")
        self.assertEqual(r.returncode, 0, r.stderr)
        path = self.log / "0007-saved-jobs-live-in-their-own-table-not.md"
        self.assertEqual(r.stdout.strip(), str(path.relative_to(self.repo)).replace("\\", "/"))
        self.assertEqual(path.read_text(encoding="utf-8"),
                         "# D-007 — Saved jobs live in their own table, not a flag on jobs\n\n"
                         "**Status:** Proposed (2026-10-16).\n"
                         "**Decided by:** dantelyro — Grade 1: asked in session.\n\n"
                         "**Context:** M1 showed it.\n\n"
                         "**Options:** (a) one; (b) two.\n\n"
                         "**Decision:** (b), because.\n\n"
                         "**Trade-offs:** Slower.\n")

    def test_the_slug_drops_punctuation_and_code_marks(self):
        r = self.new("`implement` never writes code, tests or specs; the plan is the record")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.log / "0001-implement-never-writes-code-tests-or-specs-the.md").exists())

    def test_an_apostrophe_does_not_split_a_word(self):
        r = self.new("The log’s index and the developer's yes")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.log / "0001-the-logs-index-and-the-developers-yes.md").exists())

    def test_creates_the_folder(self):
        r = self.new("First")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertTrue((self.log / "0001-first.md").exists())

    def test_every_field_is_required(self):
        r = run("decision_new.py", "--title", "T", "--context", "c", cwd=self.repo)
        self.assertNotEqual(r.returncode, 0)
        self.assertFalse(self.log.exists())


TABLE = "| Id | Title | Status |\n| --- | --- | --- |\n"


class Index(Base):
    def index(self, *args):
        return run("decision_index.py", *args, cwd=self.repo)

    def entries(self):
        self.write("0001-first.md", entry(1, "First"))
        self.write("0002-second.md", entry(2, "Second", "**SUPERSEDED by D-003 (2026-10-15).** It was wrong."))
        self.write("0002b-between.md", entry(2, "Between", "Open."))
        self.write("0003-third.md", entry(3, "Third, with a comma", "Proposed (2026-10-16)."))

    ROWS = ("| [D-001](0001-first.md) | First | Accepted |\n"
            "| [D-002](0002-second.md) | Second | SUPERSEDED by D-003 |\n"
            "| [D-002b](0002b-between.md) | Between | Open |\n"
            "| [D-003](0003-third.md) | Third, with a comma | Proposed |\n")

    def test_rebuilds_the_table_and_keeps_the_text_around_it(self):
        self.entries()
        self.write("README.md", "# Decision log\n\nIntro.\n\n" + TABLE + "| [D-001](x.md) | Stale | Open |\n\n## Conventions\n\nKeep.\n")
        r = self.index()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual((self.log / "README.md").read_text(encoding="utf-8"),
                         "# Decision log\n\nIntro.\n\n" + TABLE + self.ROWS + "\n## Conventions\n\nKeep.\n")

    def test_a_log_without_a_readme_gets_one(self):
        self.entries()
        self.assertEqual(self.index().returncode, 0)
        text = (self.log / "README.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# Decision log\n"))
        self.assertIn(TABLE + self.ROWS, text)

    def test_check_reports_a_stale_index_and_writes_nothing(self):
        self.entries()
        stale = "# Decision log\n\n" + TABLE + "| [D-001](0001-first.md) | First | Accepted |\n"
        self.write("README.md", stale)
        r = self.index("--check")
        self.assertEqual(r.returncode, 1)
        self.assertEqual((self.log / "README.md").read_text(encoding="utf-8"), stale)
        self.assertEqual(self.index().returncode, 0)
        self.assertEqual(self.index("--check").returncode, 0)

    def test_keeps_crlf_line_endings(self):
        self.entries()
        (self.log / "README.md").write_bytes(("# Decision log\r\n\r\n" + TABLE.replace("\n", "\r\n")).encode())
        self.assertEqual(self.index().returncode, 0)
        raw = (self.log / "README.md").read_bytes()
        self.assertNotIn(b"\n", raw.replace(b"\r\n", b""))
        self.assertIn(b"| [D-003](0003-third.md) | Third, with a comma | Proposed |\r\n", raw)

    def test_what_an_entry_supersedes_is_carried_into_its_status(self):
        self.write("0005-new.md", entry(5, "New", "Accepted (2026-10-15). Supersedes **D-001**, D-002b.\n"))
        self.assertEqual(self.index().returncode, 0)
        self.assertIn("| [D-005](0005-new.md) | New | Accepted, supersedes D-001, D-002b |\n",
                      (self.log / "README.md").read_text(encoding="utf-8"))

    def test_an_entry_without_a_title_line_is_an_error(self):
        self.write("0001-first.md", "no heading\n")
        r = self.index()
        self.assertEqual(r.returncode, 1)
        self.assertIn("0001-first.md", r.stdout + r.stderr)


class DevflowsOwnLog(unittest.TestCase):
    def test_the_generated_index_is_the_committed_one(self):
        r = run("decision_index.py", "--check", cwd=ROOT)
        self.assertEqual(r.returncode, 0, r.stdout + r.stderr)


if __name__ == "__main__":
    unittest.main()
