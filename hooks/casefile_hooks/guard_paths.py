"""PreToolUse on Edit, Write and NotebookEdit: where the reviewer may write.

The reviewer breaks product code in the developer's checkout and restores it; it never changes a
test, a record or settings (GUARD-001, GUARD-002). Every other session, the main one and any other
agent, is not restricted here (GUARD-009, D-074).
"""

import os
import re

from casefile_hooks import lib
from casefile_hooks.pre_commit import TEST_FILE

ISSUES = "docs/issues/"  # always protected from the reviewer (0.14.0 spec, Issues)


def _in_a_claude_folder(path: str, rel: str | None) -> bool:
    if rel is not None:
        return rel == ".claude" or rel.startswith(".claude/")
    return ".claude" in re.split(r"[\/]+", os.path.normpath(path))


def main(event: dict) -> None:
    if lib.casefile_agent(event) != "reviewer":
        lib.allow()

    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    rel = lib.repo_relative(event, path)

    if _in_a_claude_folder(path, rel):
        lib.deny(f"the reviewer may not change a `.claude` folder (agents, skills, hooks, settings): "
                 f"`{rel or path}`. Report what you need in your findings instead.")
    if rel is None or lib.git_root(event.get("cwd") or os.getcwd()) is None:
        lib.deny("the reviewer breaks code only inside the repository it reviews, where it restores "
                 f"them; `{rel or path}` is not in it. Put the problem in your findings instead.")
    cfg = lib.config(event)
    folders = [ISSUES, cfg["plans_dir"].strip("/") + "/", cfg["specs_dir"].strip("/") + "/"]
    folders += [p.strip("/") + "/" for p in cfg["protected_paths"]]
    if TEST_FILE.search(rel) or any(rel.startswith(f) for f in folders):
        lib.deny(f"the reviewer breaks product code; it never edits tests or records (`{rel}`). "
                 "Report a weak test or a wrong record as a finding instead.")
    lib.allow()
