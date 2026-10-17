"""issues_status.py — the mechanical half of docs/issues/. Run from inside the repository.

  issues_status.py                      open and in-progress issues, what each blocks, and errors
  issues_status.py --blocks PLAN TASK   the open issues blocking that task
  issues_status.py --next-id            the next free issue id and file prefix
  add --json for machine-readable output.

A `fixed (<commit>)` issue is checked, not believed: the commit must exist and be on the default
branch, and every name in backticks under "Test that must fail first" that is not a path must be
found in the default branch's files. Exit 1 when any issue has an error.

Standard library only (D-027).
"""

import argparse
import json
import os
import re
import subprocess
import sys

ISSUES_DIR = "docs/issues"
FILE = re.compile(r"^(\d{4})([a-z]?)-[a-z0-9-]+\.md$")
TITLE = re.compile(r"^# (I-(\d{4})([a-z]?)) — (.+)$")
FIELD = re.compile(r"^- (Status|Found|Blocks|Related to|Rules):\s*(.*)$")
STATUS = re.compile(r"^(open|in-progress)$|^fixed \(([0-9a-f]{7,40})\)$|^wontfix: (.+)$")
SECTIONS = ("What happens", "What should happen", "How to see it", "Test that must fail first")
BACKTICKED = re.compile(r"`([^`]+)`")


def git(root, *args):
    return subprocess.run(["git", "-C", root, *args], capture_output=True, text=True,
                          encoding="utf-8", errors="replace")


def repo_root() -> str:
    out = git(os.getcwd(), "rev-parse", "--show-toplevel")
    if out.returncode != 0:
        sys.exit("issues_status: not inside a git repository")
    return out.stdout.strip()


def default_branch(root: str) -> str:
    try:
        with open(os.path.join(root, ".claude", "devflow.json"), encoding="utf-8") as f:
            return json.load(f).get("default_branch") or "main"
    except (OSError, ValueError):
        return "main"


def parse(path: str, name: str) -> tuple[dict | None, list[str]]:
    """(issue, errors) for one file."""
    m = FILE.match(name)
    if not m:
        return None, [f"{name}: file name is not NNNN-kebab-slug.md"]
    lines = open(path, encoding="utf-8").read().splitlines()
    title = TITLE.match(lines[0]) if lines else None
    if not title:
        return None, [f"{name}: first line must be `# I-NNNN — Title`"]
    if (title.group(2), title.group(3)) != (m.group(1), m.group(2)):
        return None, [f"{name}: its id {title.group(1)} does not match the file number"]
    fields = {f.group(1): f.group(2).strip() for f in map(FIELD.match, lines) if f}
    errors = []
    for key in ("Status", "Found", "Blocks", "Related to", "Rules"):
        if key not in fields:
            errors.append(f"{name}: missing `- {key}:` line")
    headings = {line[3:].strip() for line in lines if line.startswith("## ")}
    for section in SECTIONS:
        if section not in headings:
            errors.append(f"{name}: missing `## {section}` section")
    status = STATUS.match(fields.get("Status", ""))
    if "Status" in fields and not status:
        errors.append(f"{name}: status `{fields['Status']}` is not open, in-progress, "
                      "fixed (<commit>) or wontfix: <reason>")
    test_section, inside = [], False
    for line in lines:
        if line.startswith("## "):
            inside = line[3:].strip() == "Test that must fail first"
        elif inside:
            test_section.append(line)
    blocks = fields.get("Blocks", "none")
    return {
        "id": title.group(1), "title": title.group(4), "file": f"{ISSUES_DIR}/{name}",
        "status": "fixed" if status and status.group(2) else
                  "wontfix" if status and status.group(3) else fields.get("Status"),
        "commit": status.group(2) if status else None,
        "blocks": None if blocks.lower() in ("none", "") else blocks,
        "tests": BACKTICKED.findall("\n".join(test_section)),
    }, errors


def check_fixed(root: str, branch: str, issue: dict) -> list[str]:
    name, commit = issue["file"], issue["commit"]
    if git(root, "cat-file", "-e", f"{commit}^{{commit}}").returncode != 0:
        return [f"{name}: fixed in `{commit}`, but no such commit exists"]
    if git(root, "merge-base", "--is-ancestor", commit, branch).returncode != 0:
        return [f"{name}: fixed in `{commit}`, but that commit is not on `{branch}`"]
    names = [t for t in issue["tests"] if not re.search(r"[\\/]|\.\w{1,5}$", t)]
    if not names:
        return [f"{name}: names no test (in backticks) under `## Test that must fail first`"]
    errors = []
    for test in names:
        if git(root, "grep", "-q", "-F", "-e", test, branch).returncode != 0:
            errors.append(f"{name}: the test `{test}` is not in any file on `{branch}`")
    return errors


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--blocks", nargs=2, metavar=("PLAN", "TASK"))
    ap.add_argument("--next-id", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    root = repo_root()
    folder = os.path.join(root, *ISSUES_DIR.split("/"))
    names = sorted(n for n in (os.listdir(folder) if os.path.isdir(folder) else []) if n.endswith(".md"))

    if args.next_id:
        highest = max((int(m.group(1)) for m in map(FILE.match, names) if m), default=0)
        out = {"next_id": f"I-{highest + 1:04d}", "next_file_prefix": f"{highest + 1:04d}"}
        print(json.dumps(out) if args.json else f"{out['next_id']}  ({out['next_file_prefix']}-<slug>.md)")
        return

    issues, errors = [], []
    branch = default_branch(root)
    for n in names:
        issue, problems = parse(os.path.join(folder, n), n)
        errors += problems
        if issue:
            issues.append(issue)
            if issue["status"] == "fixed" and not problems:
                errors += check_fixed(root, branch, issue)
    open_issues = [i for i in issues if i["status"] in ("open", "in-progress")]

    if args.blocks:
        target = " ".join(args.blocks)
        out = {"blocking": [i["id"] for i in open_issues if i["blocks"] == target], "errors": errors}
    else:
        out = {"open": [{k: i[k] for k in ("id", "title", "status", "blocks", "file")} for i in open_issues],
               "errors": errors}

    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        if "blocking" in out:
            print("blocking: " + (", ".join(out["blocking"]) or "none"))
        else:
            for i in out["open"]:
                print(f"{i['id']} [{i['status']}] {i['title']}" + (f" — blocks {i['blocks']}" if i["blocks"] else ""))
            if not out["open"]:
                print("no open issues")
        for e in errors:
            print(f"ERROR {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # readers decode UTF-8, whatever the console uses
    main()
