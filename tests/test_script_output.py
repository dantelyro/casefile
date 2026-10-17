"""Skill scripts print UTF-8 even where the console's code page is not (GitHub's Windows runners)."""

import os
import pathlib
import subprocess
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = sorted((ROOT / "skills").glob("*/scripts/*.py"))


class Utf8Output(unittest.TestCase):
    def test_every_script_prints_utf8_under_a_legacy_code_page(self):
        self.assertTrue(SCRIPTS)
        env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
        for script in SCRIPTS:
            with self.subTest(script.name):
                r = subprocess.run([sys.executable, str(script), "--help"], cwd=ROOT, env=env,
                                   capture_output=True)
                self.assertEqual(r.returncode, 0, r.stderr.decode("utf-8", "replace"))
                text = r.stdout.decode("utf-8")  # raises if a character came out in cp1252
                if script.name != "decision_next_id.py":  # it takes a folder, not options
                    self.assertTrue(any(ord(c) > 127 for c in text), text)  # "—" or "…" in each description


if __name__ == "__main__":
    unittest.main()
