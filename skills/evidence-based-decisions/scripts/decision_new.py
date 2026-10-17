"""decision_new.py --title … --context … --options … --decision … --trade-offs … --decided-by …

Writes the next decision entry, `Status: Proposed`, in the log's format
(references/decision-log.md) and prints its path. The file is `NNNN-<slug>.md`, the slug from the
title's first eight words. It becomes `Accepted` when the developer says yes; `Implemented by` is
added once something implements it. Standard library only.
"""

import argparse
import datetime
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from decision_next_id import next_id  # noqa: E402


def slug(title: str) -> str:
    return "-".join(re.sub(r"[^a-z0-9]+", " ", re.sub(r"['’]", "", title.lower())).split()[:8])


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for field in ("title", "context", "options", "decision", "trade-offs", "decided-by"):
        ap.add_argument(f"--{field}", required=True)
    ap.add_argument("--dir", default=os.path.join("docs", "decisions"))
    ap.add_argument("--date", default=datetime.date.today().isoformat())
    a = ap.parse_args()

    did = next_id(a.dir)
    path = os.path.join(a.dir, f"{int(did[2:]):04d}-{slug(a.title)}.md")
    text = (f"# {did} — {a.title}\n\n"
            f"**Status:** Proposed ({a.date}).\n"
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
    main()
