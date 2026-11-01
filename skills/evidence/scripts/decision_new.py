"""decision_new.py --title … --context … --options … --decision … --trade-offs … --decided-by …

Writes the next decision entry in the log's format (references/decision-log.md) and prints its
path: `Status: Proposed`, or `--status Accepted` for a decision the developer has already made, or
`--status Open`. The file is `NNNN-<slug>.md`, the slug from the title's first eight words, and its
number is one past the highest `NNNN-` filename: letter-suffixed entries (`0013b-…`) sit between two
ids and never raise it. `Implemented by` is added once something implements it. Standard library
only.
"""

import argparse
import datetime
import os
import re
import sys

ENTRY = re.compile(r"^(\d{4})-.+\.md$")


def next_id(folder: str) -> str:
    names = os.listdir(folder) if os.path.isdir(folder) else []
    nums = [int(m.group(1)) for m in map(ENTRY.match, names) if m]
    return f"D-{max(nums, default=0) + 1:03d}"


def slug(title: str) -> str:
    return "-".join(re.sub(r"[^a-z0-9]+", " ", re.sub(r"['’]", "", title.lower())).split()[:8])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for field in ("title", "context", "options", "decision", "trade-offs", "decided-by"):
        ap.add_argument(f"--{field}", required=True)
    ap.add_argument("--dir", default=os.path.join("docs", "decisions"))
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    ap.add_argument("--status", choices=("Proposed", "Accepted", "Open"), default="Proposed")
    a = ap.parse_args()

    did = next_id(a.dir)
    path = os.path.join(a.dir, f"{int(did[2:]):04d}-{slug(a.title)}.md")
    text = (f"# {did} — {a.title}\n\n"
            f"**Status:** {a.status} ({a.date}).\n"
            f"**Decided by:** {a.decided_by}\n\n"
            f"**Context:** {a.context}\n\n"
            f"**Options:** {a.options}\n\n"
            f"**Decision:** {a.decision}\n\n"
            f"**Trade-offs:** {a.trade_offs}\n")
    os.makedirs(a.dir, exist_ok=True)
    try:
        with open(path, "x", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except FileExistsError:
        sys.exit(f"{path} already exists")
    print(path.replace(os.sep, "/"))


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")  # readers decode UTF-8, whatever the console uses
    main()
