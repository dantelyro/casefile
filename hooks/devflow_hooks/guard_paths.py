"""PreToolUse on Edit, Write and NotebookEdit: which files each kind of session may write.

The developer's own session is not restricted here. No agent changes a `.claude` folder — its own
rules, the project's settings, or the user's. devflow's agents have their own limits; other agents
get only the `.claude` rule.
"""

import os
import re

from devflow_hooks import lib

ISSUES = "docs/issues/"  # always protected from devflow agents (0.14.0 spec, Issues)


def _in_a_claude_folder(path: str, rel: str | None) -> bool:
    if rel is not None:
        return rel == ".claude" or rel.startswith(".claude/")
    return ".claude" in re.split(r"[\\/]+", os.path.normpath(path))


def main(event: dict) -> None:
    agent = lib.agent_of(event)
    if not agent:
        lib.allow()

    tool_input = event.get("tool_input") or {}
    path = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
    rel = lib.repo_relative(event, path)
    role = lib.devflow_agent(event)

    if _in_a_claude_folder(path, rel):
        lib.deny(f"agents may not change a `.claude` folder (agents, skills, hooks, settings): `{rel or path}`. "
                 "Report what you need in your output instead.")

    if role is None:
        lib.allow()

    if role == "reviewer":
        lib.deny("the reviewer never edits files. Put the problem in your findings instead.")

    if rel is None:
        lib.deny(f"the {role} only writes inside the repository it works in; `{path}` is outside it.")

    cfg = lib.config(event)

    if role == "planner":
        plans = cfg["plans_dir"].strip("/") + "/"
        if not (rel.startswith(plans) and rel.endswith(".md") and "/" not in rel[len(plans):]):
            lib.deny(f"the planner only writes its plan file, `{plans}<scope>.md`, not `{rel}`.")
        lib.allow()

    if rel.startswith(ISSUES):
        lib.deny(f"devflow agents do not write issues (`{rel}`). Report the bug in your NOTES, with what "
                 "happens, what should happen and how to see it; the main session files it after the "
                 "developer agrees.")

    for protected in cfg["protected_paths"]:
        prefix = protected.strip("/") + "/"
        if rel.startswith(prefix):
            lib.deny(f"devflow agents may not edit `{prefix}` (`{rel}`). If it is wrong or missing "
                     "something, report STATUS: blocked with the question.")

    lib.allow()
