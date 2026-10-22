"""Skill scripts print UTF-8 even where the console's code page is not (GitHub's Windows runners)."""

import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPTS = sorted((ROOT / "plugins" / "devflow" / "skills").glob("*/scripts/*.py"))


def test_there_are_skill_scripts_to_check():
    assert SCRIPTS


@pytest.mark.parametrize("script", SCRIPTS, ids=lambda s: s.name)
def test_every_script_prints_utf8_under_a_legacy_code_page(script):
    env = dict(os.environ, PYTHONIOENCODING="cp1252", PYTHONUTF8="0")
    r = subprocess.run([sys.executable, str(script), "--help"], cwd=ROOT, env=env,
                       capture_output=True, check=False)
    assert r.returncode == 0, r.stderr.decode("utf-8", "replace")
    text = r.stdout.decode("utf-8", errors="replace")  # a character that came out in cp1252 becomes U+FFFD
    assert "�" not in text, f"{script.name} printed a non-UTF-8 byte: {text!r}"
    if script.name != "decision_next_id.py":  # it takes a folder, not options
        assert any(ord(c) > 127 for c in text), text  # "—" or "…" in each description
