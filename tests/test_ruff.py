"""TOOL-001: the code passes ruff's default rules.

Plain functions, standard library only: the unittest gate does not collect them.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _ruff_check(folder):
    return subprocess.run(
        ["uv", "run", "ruff", "check", folder],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )


def test_TOOL_001_hooks_pass_ruff():
    result = _ruff_check("hooks")
    assert result.returncode == 0, result.stdout + result.stderr
