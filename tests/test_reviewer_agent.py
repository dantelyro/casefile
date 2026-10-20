"""The reviewer agent file: what a file can show of REV-001..REV-008 (all [MANUAL] except REV-007)."""
import re
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent / "agents" / "reviewer.md"


def _text():
    return AGENT.read_text(encoding="utf-8")


def _tools(text):
    m = re.match(r"---\n(.*?)\n---", text, re.S)
    assert m, "no frontmatter in agents/reviewer.md"
    line = [l for l in m.group(1).splitlines() if l.startswith("tools:")]
    assert line, "no tools line in agents/reviewer.md"
    return [t.strip() for t in line[0].split(":", 1)[1].split(",")]


def _output_block(text):
    m = re.search(r"## Output.*?```\n(.*?)```", text, re.S)
    assert m, "no output block in agents/reviewer.md"
    return m.group(1)


class Reviewer(unittest.TestCase):
    def test_REV_001_reviewer_has_the_edit_tool(self):
        tools = _tools(_text())
        self.assertIn("Edit", tools)
        self.assertNotIn("Write", tools)

    def test_REV_006_reviewer_report_has_a_breaks_line_with_git_status(self):
        lines = _output_block(_text()).splitlines()
        # VERDICT is asserted to prove the block was found and parsed
        self.assertTrue([l for l in lines if l.startswith("VERDICT:")])
        breaks = [l for l in lines if l.startswith("BREAKS:")]
        self.assertTrue(breaks)
        self.assertIn("git status: clean", breaks[0])


if __name__ == "__main__":
    unittest.main()
