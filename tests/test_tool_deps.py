"""TOOL-005: ruff and pytest are uv dev dependencies, pinned by a committed lock.

Plain functions, standard library only: the unittest gate does not collect them.
"""

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def _run(args):
    return subprocess.run(
        args, cwd=ROOT, capture_output=True, text=True, timeout=120, check=False
    )


def test_TOOL_005_ruff_and_pytest_are_dev_dependencies_in_a_current_lock():
    result = _run(["uv", "export", "--locked", "--only-group", "dev", "--no-hashes"])
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert any(line.startswith("ruff==") for line in lines), result.stdout
    assert any(line.startswith("pytest==") for line in lines), result.stdout


def test_TOOL_005_uv_lock_is_committed():
    result = _run(["git", "ls-files", "--error-unmatch", "uv.lock"])
    assert result.returncode == 0, result.stderr


def test_TOOL_005_venv_is_ignored():
    lines = (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
    assert ".venv/" in lines
