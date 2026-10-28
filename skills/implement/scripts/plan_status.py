"""plan_status.py PLAN — where a plan stands. Run from inside the repository.

  ready        todo tasks whose dependencies are all done and that no open issue blocks
  batch        the first ready task plus the ready tasks it lists as parallel-safe (--max, default 3)
  in_progress  tasks an earlier session left in progress (the resume rule looks at their branches)
  waiting      todo tasks held by an open issue in docs/issues/ (Blocks: <plan> <task>), or by an
               entry of the plan's Blockers named in their Depends on (`needs Gabriel (B18)`)
  blocked      tasks marked `blocked: <reason>`
  choices      every `Planner choice:` in a task's Notes — something no spec rule states, which the
               developer accepts or cuts when the plan is approved
  elsewhere    tasks whose `Repo:` is a sibling repository, with their status read from the sibling's
               copy of the plan (same path); they are built there, never here
add --json for machine-readable output. Exit 1 when the plan cannot be read or has errors.

Open issues are read through fix-bug's issues_status.py, never parsed twice. Standard library only.
"""

import argparse
import json
import os
import pathlib
import re
import subprocess
import sys

TASK = re.compile(r"^### ([A-Z]\d+[a-z]?) · (.+)$")  # T3, F1 (fix tasks), T3b
FIELD = re.compile(r"^- (Status|Depends on|Parallel-safe with|Repo|Notes):\s*(.*)$")
STATUS = re.compile(r"^(todo|in-progress)$|^done \(([0-9a-f]{7,40})\)$|^blocked: (.+)$")
CHOICE = re.compile(r"Planner choice:\s*", re.IGNORECASE)
ISSUES_STATUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "fix-bug", "scripts", "issues_status.py")


def task_ids(text: str) -> list[str]:
    if text.strip().lower().startswith("none") or not text.strip():
        return []
    return re.findall(r"(?<![\w-])[A-Z]\d+[a-z]?(?![\w-])", text)


def plan_blockers(plan_text: str) -> set[str]:
    """IDs that open an item of the `## Blockers` section: `- B18 (needs Gabriel): ...`."""
    m = re.search(r"^## Blockers\s*$(.*?)(?=^## |\Z)", plan_text, re.MULTILINE | re.DOTALL)
    if not m:
        return set()
    return set(re.findall(r"^\s*[-*]\s+\**([A-Z]\d+[a-z]?)(?![\w-])", m.group(1), re.MULTILINE))


def parse(plan_text: str) -> tuple[list[dict], list[str]]:
    tasks, errors, current = [], [], None
    for line in plan_text.splitlines():
        m = TASK.match(line)
        if m:
            current = {"id": m.group(1), "title": m.group(2), "status": None, "depends": [], "parallel": [], "blockers": [],
                       "repo": None}
            tasks.append(current)
        elif line.startswith("## "):
            current = None
        elif current is not None:
            f = FIELD.match(line)
            if f and f.group(1) == "Status":
                current["status_text"] = f.group(2).strip()
            elif f and f.group(1) == "Depends on":
                current["depends"] = task_ids(f.group(2))
            elif f and f.group(1) == "Repo":
                current["repo"] = f.group(2).strip()
            elif f and f.group(1) == "Notes":
                current["choices"] = [c.strip() for c in CHOICE.split(f.group(2))[1:] if c.strip()]
            elif f:
                current["parallel"] = task_ids(f.group(2))
    known = {t["id"] for t in tasks}
    blockers = plan_blockers(plan_text)
    for t in tasks:
        s = STATUS.match(t.get("status_text", ""))
        if not s:
            errors.append(f"{t['id']}: status `{t.get('status_text', '')}` is not todo, in-progress, "
                          "done (<commit>) or blocked: <reason>")
            continue
        t["status"] = s.group(1) or ("done" if s.group(2) else "blocked")
        t["reason"] = s.group(3)
        t["blockers"] = [d for d in t["depends"] if d in blockers and d not in known]
        t["depends"] = [d for d in t["depends"] if d not in t["blockers"]]
        for dep in t["depends"]:
            if dep not in known:
                errors.append(f"{t['id']}: depends on {dep}, which is not in the plan")
    return tasks, errors


def config(root: str) -> dict:
    try:
        with open(os.path.join(root, ".claude", "casefile.json"), encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def take_sibling_statuses(tasks: list[dict], plan: str, errors: list[str]) -> list[dict]:
    """Marks the tasks another repository builds, with the status its own copy of the plan gives."""
    root = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                          text=True, check=False).stdout.strip() or os.getcwd()
    cfg = config(root)
    siblings = cfg.get("siblings") or {}
    if not siblings:
        return []
    here = cfg.get("repo")
    if not here:
        errors.append("casefile.json declares `siblings` but not `repo`, this repository's name in them")
        return []
    rel = os.path.relpath(os.path.abspath(plan), root)
    copies: dict[str, dict] = {}
    elsewhere = []
    for t in tasks:
        name = t["repo"]
        if name in (None, here):
            continue
        if name not in siblings:
            errors.append(f"{t['id']}: Repo `{name}` is neither `{here}` nor a sibling in casefile.json")
            continue
        if name not in copies:
            path = os.path.join(root, siblings[name], rel)
            try:
                copies[name] = {s["id"]: s for s in parse(pathlib.Path(path).read_text(encoding="utf-8"))[0]}
            except OSError as e:
                copies[name] = {}
                errors.append(f"{name}: its copy of the plan, {path}, cannot be read: {e.strerror}")
                continue
        theirs = copies[name].get(t["id"])
        if copies[name] and not theirs:
            errors.append(f"{t['id']}: not in {name}'s copy of the plan")
        t["status"], t["reason"] = (theirs["status"], theirs["reason"]) if theirs else (None, None)
        t["elsewhere"] = True
        elsewhere.append({"task": t["id"], "repo": name, "status": t["status"]})
    return elsewhere


def blocking_issues(plan: str, task: str) -> list[str]:
    if not os.path.isdir(os.path.join("docs", "issues")):
        return []
    out = subprocess.run([sys.executable, ISSUES_STATUS, "--blocks", plan, task, "--json"],
                         capture_output=True, text=True, encoding="utf-8", check=False)
    try:
        return json.loads(out.stdout)["blocking"]
    except (ValueError, KeyError):
        sys.exit(f"plan_status: issues_status.py failed: {out.stderr.strip() or out.stdout.strip()}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("plan")
    ap.add_argument("--max", type=int, default=3)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    plan = args.plan.replace("\\", "/")
    try:
        text = pathlib.Path(plan).read_text(encoding="utf-8")
    except OSError as e:
        print(json.dumps({"errors": [f"{plan}: {e.strerror}"]}) if args.json else f"ERROR {plan}: {e.strerror}")
        sys.exit(1)
    tasks, errors = parse(text)
    elsewhere = take_sibling_statuses(tasks, plan, errors)
    by_id = {t["id"]: t for t in tasks}
    here = [t for t in tasks if not t.get("elsewhere")]

    ready, waiting = [], []
    for t in here:
        if t["status"] != "todo" or any(by_id.get(d, {}).get("status") != "done" for d in t["depends"]):
            continue
        held = blocking_issues(plan, t["id"])
        if held or t["blockers"]:
            waiting.append({"task": t["id"], "issues": held, "blockers": t["blockers"]})
        else:
            ready.append(t["id"])
    batch = []
    if ready:
        first = by_id[ready[0]]
        batch = [first["id"]] + [p for p in first["parallel"] if p in ready]
        batch = batch[:max(args.max, 1)]

    out = {
        "ready": ready, "batch": batch,
        "in_progress": [t["id"] for t in here if t["status"] == "in-progress"],
        "waiting": waiting,
        "blocked": [{"task": t["id"], "reason": t["reason"]} for t in here if t["status"] == "blocked"],
        "done": [t["id"] for t in here if t["status"] == "done"],
        "choices": [{"task": t["id"], "choice": c} for t in tasks for c in t.get("choices", [])],
        "elsewhere": elsewhere,
        "errors": errors,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("batch: " + (", ".join(batch) or "none"))
        print("ready: " + (", ".join(ready) or "none"))
        print("in progress: " + (", ".join(out["in_progress"]) or "none"))
        for w in waiting:
            print(f"waiting: {w['task']} on " + ", ".join(w["issues"] + [f"{b} (Blockers)" for b in w["blockers"]]))
        for b in out["blocked"]:
            print(f"blocked: {b['task']} — {b['reason']}")
        for c in out["choices"]:
            print(f"planner choice: {c['task']} — {c['choice']}")
        for e in elsewhere:
            print(f"elsewhere: {e['task']} in {e['repo']} — {e['status'] or 'unknown'}")
        print(f"done: {len(out['done'])} of {len(here)}" + (" here" if elsewhere else ""))
        for e in errors:
            print(f"ERROR {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # readers decode UTF-8, whatever the console uses
    main()
