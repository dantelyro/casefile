"""rules_coverage.py PLAN — which rules in a plan's scope have a test named after them.

The scope is the plan's `## Rules covered` section. Each rule's tag comes from its heading in the
specs folder (`specs_dir`, default docs/specs): `### MATCH-010 · Title     [MVP]`.

  covered    [MVP] rules with a test named after them
  missing    [MVP] rules with none — exit 1
  manual     [MANUAL] rules: checked in review, never missing
  later      [LATER] rules: out of scope
  untracked  rules in scope with no heading in the specs (a table row, say): reported with whether
             a test names them, never failed

A test is named after a rule when a test file holds `it('MATCH-010: …'` / `test("MATCH-010 …"`
(Jest, Vitest, Playwright) or `def test_MATCH_010_…` (pytest, unittest). Comments do not count.
Files are the repository's, minus what .gitignore ignores. Standard library only.
"""

import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_RULE = r"[A-Z]+-\d{3}"
TEST_FILE = re.compile(r"\.(test|spec)\.([cm]?[jt]s|[jt]sx)$|(^|/)test_[^/]*\.py$|_test\.py$")
TAG = re.compile(r"\[([A-Z]+)\]")
JS_COMMENTS = re.compile(r"/\*.*?\*/|(^|\s)//[^\n]*", re.DOTALL)
PY_COMMENTS = re.compile(r"(^|\s)#[^\n]*")


def config(root: str) -> dict:
    try:
        with open(os.path.join(root, ".claude", "devflow.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                          text=True).stdout.strip() or os.getcwd()
    cfg = config(root)
    rule = cfg.get("rule_id_pattern") or DEFAULT_RULE
    specs_dir = os.path.join(root, *(cfg.get("specs_dir") or "docs/specs").split("/"))
    errors = []

    try:
        plan_text = open(args.plan, encoding="utf-8").read()
    except OSError as e:
        plan_text, errors = "", [f"{args.plan}: {e.strerror}"]
    scope: list[str] = []
    m = re.search(r"^## Rules covered\s*$(.*?)(?=^## |\Z)", plan_text, re.M | re.S)
    if m:
        for line in m.group(1).splitlines():
            if line.startswith("- "):
                head = line[2:].split("→")[0]
                scope += [r for r in re.findall(rf"(?<![\w-])({rule})(?![\w-])", head) if r not in scope]
    elif not errors:
        errors.append(f"{args.plan}: no `## Rules covered` section")

    tags: dict[str, set[str]] = {}
    heading = re.compile(rf"^### ({rule})\b(.*)$")
    for name in sorted(os.listdir(specs_dir)) if os.path.isdir(specs_dir) else []:
        if name.endswith(".md") and name.lower() != "readme.md":
            for line in open(os.path.join(specs_dir, name), encoding="utf-8").read().splitlines():
                h = heading.match(line)
                if h:
                    tags[h.group(1)] = set(TAG.findall(h.group(2)))

    files = subprocess.run(["git", "-C", root, "ls-files", "--cached", "--others", "--exclude-standard"],
                           capture_output=True, text=True, encoding="utf-8").stdout.splitlines()
    named: set[str] = set()
    js_name = re.compile(rf"""(?<![.\w])(?:it|test)(?:\.\w+)*\s*\(\s*["'`]({rule})[:\s]""")
    py_name = re.compile(r"^\s*(?:async\s+)?def test_([A-Z]+)_(\d+)_", re.M)
    for rel in files:
        if not TEST_FILE.search(rel):
            continue
        try:
            text = open(os.path.join(root, rel), encoding="utf-8").read()
        except (OSError, UnicodeDecodeError):
            continue
        if rel.endswith(".py"):
            named |= {f"{a}-{b}" for a, b in py_name.findall(PY_COMMENTS.sub(r"\1", text))}
        else:
            named |= set(js_name.findall(JS_COMMENTS.sub(r"\1", text)))

    out = {"covered": [], "missing": [], "manual": [], "later": [], "untracked": [], "errors": errors}
    for r in scope:
        if r not in tags:
            out["untracked"].append({"rule": r, "tested": r in named})
        elif "MANUAL" in tags[r]:
            out["manual"].append(r)
        elif "MVP" in tags[r]:
            out["covered" if r in named else "missing"].append(r)
        else:
            out["later"].append(r)

    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"covered ({len(out['covered'])}): " + (", ".join(out["covered"]) or "none"))
        print(f"MISSING ({len(out['missing'])}): " + (", ".join(out["missing"]) or "none"))
        print("checked in review: " + (", ".join(out["manual"]) or "none"))
        if out["later"]:
            print("later: " + ", ".join(out["later"]))
        for u in out["untracked"]:
            print(f"untracked (no heading in the specs): {u['rule']} — {'has a test' if u['tested'] else 'no test'}")
        for e in errors:
            print(f"ERROR {e}")
    sys.exit(1 if out["missing"] or errors else 0)


if __name__ == "__main__":
    main()
