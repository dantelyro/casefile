"""spec_lint.py [--json] — check that a project's specs hold together.

- every rule heading parses: `### MATCH-010 · Title`, optionally followed by tags (other `###`
  headings are not rules);
- rule IDs are unique across the spec files;
- every tag is LATER, VERIFY or MANUAL, and a rule may carry several (`[LATER][VERIFY]`); `[MVP]` is
  an error, since a rule needs no tag (D-049);
- every rule ID named in the build order's section exists (`build_order`, default
  docs/product/blueprint.html; HTML or Markdown). No build order file yet is a warning;
- every relative link, `D-NNN` and rule ID in docs/product/product-decisions.md reaches a file, a
  decision entry or a rule that exists;
- the specs README's file table lists exactly the spec files.

Folders come from .claude/devflow.json (`specs_dir`, `build_order`, `rule_id_pattern`). Exit 1 on
any error. Standard library only.
"""

import argparse
import json
import os
import re
import subprocess
import sys

DEFAULT_RULE = r"[A-Z]+-\d{3}"
TAGS = {"LATER", "VERIFY", "MANUAL"}
DECISION = re.compile(r"(?<![\w-])D-(\d{3,})([a-z]?)(?![\w-])")


def config(root: str) -> dict:
    try:
        with open(os.path.join(root, ".claude", "devflow.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def build_order_section(text: str, html: bool) -> str | None:
    if html:
        m = re.search(r"<(h[1-6]|span|div|p|header)\b[^>]*>\s*Build order\s*</\1>", text, re.IGNORECASE)
        if not m:
            return None
        end = text.find("</section>", m.end())
        return text[m.end(): end if end != -1 else len(text)]
    m = re.search(r"^(#+)\s*Build order\s*$", text, re.MULTILINE | re.IGNORECASE)
    if not m:
        return None
    nxt = re.search(rf"^#{{1,{len(m.group(1))}}}\s", text[m.end():], re.MULTILINE)
    return text[m.end(): m.end() + nxt.start() if nxt else len(text)]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()

    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                          text=True, check=False).stdout.strip() or os.getcwd()
    cfg = config(root)
    rule = cfg.get("rule_id_pattern") or DEFAULT_RULE
    specs_rel = (cfg.get("specs_dir") or "docs/specs").strip("/")
    order_rel = cfg.get("build_order") or "docs/product/blueprint.html"
    specs_dir = os.path.join(root, *specs_rel.split("/"))
    rule_id = re.compile(rf"(?<![\w-])({rule})(?![\w-])")
    heading_id = re.compile(rf"^###\s+({rule})(?![\w-])")
    heading = re.compile(rf"^###\s+({rule}) · (\S.*?)(?:\s+((?:\[[A-Z]+\]\s*)+))?\s*$")
    errors: list[str] = []
    warnings: list[str] = []
    rules: dict[str, str] = {}

    if not os.path.isdir(specs_dir):
        errors.append(f"{specs_rel}/: no specs folder")
        files = []
    else:
        files = sorted(n for n in os.listdir(specs_dir) if n.endswith(".md") and n.lower() != "readme.md")
    for name in files:
        for no, line in enumerate(read(os.path.join(specs_dir, name)).splitlines(), 1):
            if not heading_id.match(line):
                continue
            where = f"{specs_rel}/{name}:{no}"
            h = heading.match(line)
            if not h:
                errors.append(f"{where}: rule heading does not parse, expected "
                              f"`### {heading_id.match(line).group(1)} · Title`")
                continue
            for tag in re.findall(r"\[([A-Z]+)\]", h.group(3) or ""):
                if tag == "MVP":
                    errors.append(f"{where}: {h.group(1)} has tag [MVP]; remove it, a rule needs no tag (D-049)")
                elif tag not in TAGS:
                    errors.append(f"{where}: {h.group(1)} has tag [{tag}]; use LATER, VERIFY or MANUAL, or no tag")
            if h.group(1) in rules:
                errors.append(f"{h.group(1)} is used twice: {rules[h.group(1)]} and {where}")
            else:
                rules[h.group(1)] = where

    readme = os.path.join(specs_dir, "README.md")
    if os.path.isdir(specs_dir):
        if not os.path.exists(readme):
            errors.append(f"{specs_rel}/README.md: missing; it holds the file table")
        else:
            listed = set(re.findall(r"^\|\s*\[[^\]]*\]\(([^)#\s]+\.md)\)", read(readme), re.MULTILINE))
            for name in sorted(set(files) - listed):
                errors.append(f"{specs_rel}/README.md: file table does not list {name}")
            for name in sorted(listed - set(files)):
                errors.append(f"{specs_rel}/README.md: file table lists {name}, which does not exist")

    order_path = os.path.join(root, *order_rel.split("/"))
    if not os.path.exists(order_path):
        warnings.append(f"no build order yet ({order_rel})")
    else:
        section = build_order_section(read(order_path), order_rel.lower().endswith((".html", ".htm")))
        if section is None:
            errors.append(f"{order_rel}: no \"Build order\" section")
        else:
            for rid in sorted(set(rule_id.findall(section)) - set(rules)):
                errors.append(f"{order_rel}: the build order names {rid}, which no spec defines")

    pd_rel = "docs/product/product-decisions.md"
    pd = os.path.join(root, *pd_rel.split("/"))
    if os.path.exists(pd):
        text = read(pd)
        for target in re.findall(r"\]\(([^)\s]+)\)", text):
            if re.match(r"^[a-z][a-z0-9+.-]*:", target, re.IGNORECASE):
                continue
            path = target.split("#")[0]
            if path and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(pd), path))):
                errors.append(f"{pd_rel}: links to {path}, which does not exist")
        log = os.path.join(root, "docs", "decisions")
        names = os.listdir(log) if os.path.isdir(log) else []
        entries = {m.group(1) for m in (re.match(r"^(\d{4}[a-z]?)-.+\.md$", n) for n in names) if m}
        for num, suffix in sorted(set(DECISION.findall(text))):
            if f"{int(num):04d}{suffix}" not in entries:
                errors.append(f"{pd_rel}: names D-{num}{suffix}, which has no entry in docs/decisions/")
        for rid in sorted(set(rule_id.findall(DECISION.sub(" ", text))) - set(rules)):
            errors.append(f"{pd_rel}: names {rid}, which no spec defines")

    out = {"rules": len(rules), "errors": errors, "warnings": warnings}
    if a.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print(f"{len(rules)} rules in {len(files)} spec files")
        for w in warnings:
            print(f"WARN {w}")
        for e in errors:
            print(f"ERROR {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # readers decode UTF-8, whatever the console uses
    main()
