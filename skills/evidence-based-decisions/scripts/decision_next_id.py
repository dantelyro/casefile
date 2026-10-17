"""decision_next_id.py [DIR] — the next free decision id in a decision log (default docs/decisions).

The highest `NNNN-` filename is the pointer: one past it is next. Letter-suffixed entries
(`0013b-…`) sit between two ids and never raise it. Standard library only.
"""

import os
import re
import sys

ENTRY = re.compile(r"^(\d{4})-.+\.md$")


def next_id(folder: str) -> str:
    names = os.listdir(folder) if os.path.isdir(folder) else []
    nums = [int(m.group(1)) for m in map(ENTRY.match, names) if m]
    return f"D-{max(nums, default=0) + 1:03d}"


if __name__ == "__main__":
    print(next_id(sys.argv[1] if len(sys.argv) > 1 else os.path.join("docs", "decisions")))
