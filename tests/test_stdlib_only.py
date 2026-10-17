"""devflow's Python imports nothing outside the standard library (D-027)."""

import ast
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parent.parent
OWN = {"devflow_hooks", "run"}


class StdlibOnly(unittest.TestCase):
    def test_every_import_is_stdlib_or_devflow(self):
        files = [p for d in ("hooks", "skills", "tests") for p in (ROOT / d).rglob("*.py")]
        self.assertTrue(files)
        bad = []
        for path in files:
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
                        bad.append(f"{path.relative_to(ROOT)}: {name}")
        self.assertEqual(bad, [])


if __name__ == "__main__":
    unittest.main()
