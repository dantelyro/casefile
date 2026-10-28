"""Shipped code (hooks/ and skills/) imports only the standard library (D-027, D-048)."""

import ast
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWN = {"casefile_hooks", "run"}


SCANNED = ("hooks", "skills")


def shipped_files(root):
    return [p for d in SCANNED for p in (root / d).rglob("*.py")]


def third_party_imports(root):
    """Return `path: module` for every import in hooks/ and skills/ outside the standard library."""
    bad = []
    for path in shipped_files(root):
        tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [a.name for a in node.names]
            elif isinstance(node, ast.ImportFrom) and node.level == 0:
                names = [node.module]
            else:
                continue
            for name in names:
                top = name.split(".")[0]
                sibling = (path.parent / f"{top}.py").exists()
                if top not in sys.stdlib_module_names and top not in OWN and not sibling:
                    bad.append(f"{path.relative_to(root)}: {name}")
    return bad


def test_TOOL_004_hooks_and_skills_import_only_the_standard_library():
    assert third_party_imports(ROOT) == []
    assert shipped_files(ROOT)


def test_TOOL_004_a_third_party_import_in_shipped_code_is_reported(tmp_path):
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "x.py").write_text("import pytest\n", encoding="utf-8")
    scripts = tmp_path / "skills" / "s" / "scripts"
    scripts.mkdir(parents=True)
    (scripts / "y.py").write_text("import requests\n", encoding="utf-8")
    (scripts / "z.py").write_text("from requests import get\n", encoding="utf-8")
    found = third_party_imports(tmp_path)
    assert len(found) == 3
    assert any("x.py" in f and f.endswith(": pytest") for f in found)
    assert any("y.py" in f and f.endswith(": requests") for f in found)
    assert any("z.py" in f and f.endswith(": requests") for f in found)


def test_TOOL_004_tests_may_import_pytest(tmp_path):
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_x.py").write_text("import pytest\n", encoding="utf-8")
    (tmp_path / "hooks").mkdir()
    (tmp_path / "hooks" / "ok.py").write_text("import json\n", encoding="utf-8")
    assert third_party_imports(tmp_path) == []
