"""The implementer agent file: what a file can show of IMPL-001 and IMPL-002 (both [MANUAL])."""
import re
import unittest
from pathlib import Path

AGENT = Path(__file__).resolve().parent.parent / "agents" / "implementer.md"


def _text():
    return AGENT.read_text(encoding="utf-8")


def _output_block(text):
    m = re.search(r"## Output.*?```\n(.*?)```", text, re.S)
    assert m, "no output block in agents/implementer.md"
    return m.group(1)


class Implementer(unittest.TestCase):
    def test_IMPL_001_implementer_report_has_no_breaks_line(self):
        lines = _output_block(_text()).splitlines()
        self.assertFalse([l for l in lines if l.startswith("BREAKS:")])
        # RED is asserted to prove the block was found and parsed
        self.assertTrue([l for l in lines if l.startswith("RED:")])

    def test_IMPL_001_implementer_has_no_break_check_step(self):
        process = _text().split("## Process", 1)[1].split("\n## ", 1)[0]
        steps = re.findall(r"^\d+\. \*\*(.+?)\*\*", process, re.M)
        self.assertTrue(steps)
        self.assertNotIn("Break check.", steps)
        self.assertNotIn("break", process.lower())

    def test_IMPL_002_implementer_reports_red_none_when_behaviour_exists(self):
        text = _text()
        self.assertIn("RED: none — <test> passed on first run", text)
        after = text.split("RED: none", 1)[1].split("\n3. ", 1)[0]
        self.assertIn("you touch no product code", " ".join(after.split()))


if __name__ == "__main__":
    unittest.main()
