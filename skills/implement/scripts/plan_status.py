"""plan_status.py PLAN — where a plan stands. Run from inside the repository.

  ready        todo tasks whose dependencies are all done and that no open issue blocks
  batch        the first ready task plus the ready tasks it lists as parallel-safe (--max, default 3)
  in_progress  tasks an earlier session left in progress (the resume rule looks at their branches)
  waiting      todo tasks held by an open issue in docs/issues/ (Blocks: <plan> <task>)
  blocked      tasks marked `blocked: <reason>`
add --json for machine-readable output. Exit 1 when the plan cannot be read or has errors.

Open issues are read through fix-bug's issues_status.py, never parsed twice. Standard library only.
"""

import argparse
import json
import os
import re
import subprocess
import sys

TASK = re.compile(r"^### ([A-Z]\d+[a-z]?) · (.+)$")  # T3, F1 (fix tasks), T3b
FIELD = re.compile(r"^- (Status|Depends on|Parallel-safe with):\s*(.*)$")
STATUS = re.compile(r"^(todo|in-progress)$|^done \(([0-9a-f]{7,40})\)$|^blocked: (.+)$")
ISSUES_STATUS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "..", "..", "fix-bug", "scripts", "issues_status.py")


def task_ids(text: str) -> list[str]:
    if text.strip().lower().startswith("none") or not text.strip():
        return []
    return re.findall(r"(?<![\w-])[A-Z]\d+[a-z]?(?![\w-])", text)


def parse(plan_text: str) -> tuple[list[dict], list[str]]:
    tasks, errors, current = [], [], None
    for line in plan_text.splitlines():
        m = TASK.match(line)
        if m:
            current = {"id": m.group(1), "title": m.group(2), "status": None, "depends": [], "parallel": []}
            tasks.append(current)
        elif line.startswith("## "):
            current = None
        elif current is not None:
            f = FIELD.match(line)
            if f and f.group(1) == "Status":
                current["status_text"] = f.group(2).strip()
            elif f and f.group(1) == "Depends on":
                current["depends"] = task_ids(f.group(2))
            elif f:
                current["parallel"] = task_ids(f.group(2))
    known = {t["id"] for t in tasks}
    for t in tasks:
        s = STATUS.match(t.get("status_text", ""))
        if not s:
            errors.append(f"{t['id']}: status `{t.get('status_text', '')}` is not todo, in-progress, "
                          "done (<commit>) or blocked: <reason>")
            continue
        t["status"] = s.group(1) or ("done" if s.group(2) else "blocked")
        t["reason"] = s.group(3)
        for dep in t["depends"]:
            if dep not in known:
                errors.append(f"{t['id']}: depends on {dep}, which is not in the plan")
    return tasks, errors


def blocking_issues(plan: str, task: str) -> list[str]:
    if not os.path.isdir(os.path.join("docs", "issues")):
        return []
    out = subprocess.run([sys.executable, ISSUES_STATUS, "--blocks", plan, task, "--json"],
                         capture_output=True, text=True, encoding="utf-8")
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
        text = open(plan, encoding="utf-8").read()
    except OSError as e:
        print(json.dumps({"errors": [f"{plan}: {e.strerror}"]}) if args.json else f"ERROR {plan}: {e.strerror}")
        sys.exit(1)
    tasks, errors = parse(text)
    by_id = {t["id"]: t for t in tasks}

    ready, waiting = [], []
    for t in tasks:
        if t["status"] != "todo" or any(by_id.get(d, {}).get("status") != "done" for d in t["depends"]):
            continue
        held = blocking_issues(plan, t["id"])
        if held:
            waiting.append({"task": t["id"], "issues": held})
        else:
            ready.append(t["id"])
    batch = []
    if ready:
        first = by_id[ready[0]]
        batch = [first["id"]] + [p for p in first["parallel"] if p in ready]
        batch = batch[:max(args.max, 1)]

    out = {
        "ready": ready, "batch": batch,
        "in_progress": [t["id"] for t in tasks if t["status"] == "in-progress"],
        "waiting": waiting,
        "blocked": [{"task": t["id"], "reason": t["reason"]} for t in tasks if t["status"] == "blocked"],
        "done": [t["id"] for t in tasks if t["status"] == "done"],
        "errors": errors,
    }
    if args.json:
        print(json.dumps(out, ensure_ascii=False))
    else:
        print("batch: " + (", ".join(batch) or "none"))
        print("ready: " + (", ".join(ready) or "none"))
        print("in progress: " + (", ".join(out["in_progress"]) or "none"))
        for w in waiting:
            print(f"waiting: {w['task']} on {', '.join(w['issues'])}")
        for b in out["blocked"]:
            print(f"blocked: {b['task']} — {b['reason']}")
        print(f"done: {len(out['done'])} of {len(tasks)}")
        for e in errors:
            print(f"ERROR {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
