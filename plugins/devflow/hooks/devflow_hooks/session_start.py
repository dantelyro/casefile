"""SessionStart: point Claude at the evidence skill.

evidence-based-decisions triggers on "the start of a session", which no user prompt ever says, so
the skill never fires on its own judgement; this injects the trigger (D-003). It injects a pointer,
not the skill body, so the per-session cost stays at a few hundred tokens (D-004).
"""

import json
import os
import re
import sys
from pathlib import Path

from devflow_hooks import lib

LEGEND = re.compile(r"^✅ decided by \S.*? · ❌ rejected by \S.*?\s*$")

DIRECTIVE = """<devflow>
Invoke the `devflow:evidence-based-decisions` skill with the Skill tool now, before your first response in this session.

It triggers on the start of a session -- reconciling the context documents of a project against what has landed since they were last updated. No user prompt will ever name that, which is why this hook injects it instead.

What the skill will have you do, so you know what you are opting into:

- **The project keeps a decision log, architecture doc, or reconciliation watermark** -- replay `git log --oneline <watermark>..HEAD` over the relevant source paths, read what those commits changed, update whatever they invalidated, and move the watermark.
- **The project keeps none of those** -- propose the set and ASK, then wait for an answer before creating anything.
- **Neither applies** -- say so in one line and get on with what the user actually asked for. This is orientation, not a ceremony to perform.
</devflow>"""


def directive(event: dict) -> str:
    """Name stale formats without injecting document contents; read errors are nonblocking."""
    try:
        cwd = event.get("cwd") or os.getcwd()
        root = Path(lib.git_root(cwd) or cwd)
        stale = []
        if (root / "docs/mental-model.md").exists():
            stale.append("- docs/mental-model.md: the architecture document is now "
                         "docs/architecture/overview.md")
        decisions = root / "docs/product/product-decisions.md"
        if decisions.exists():
            lines = decisions.read_text(encoding="utf-8").splitlines()
            heading = next((i for i, line in enumerate(lines) if line.startswith("# ")), -1)
            first = next((line for line in lines[heading + 1:] if line.strip()), "")
            reasons = []
            if not LEGEND.match(first):
                reasons.append("no legend line")
            missing = [str(i) for i, line in enumerate(lines, 1)
                       if line.startswith("- ") and not line.startswith(("- ✅ ", "- ❌ "))]
            if missing:
                reasons.append(f"lines {', '.join(missing)} have no ✅ or ❌")
            if reasons:
                stale.append("- docs/product/product-decisions.md: " + "; ".join(reasons))
        if stale:
            block = "\nOut of date, rewrite in devflow's current format (D-052):\n"
            return DIRECTIVE.replace("</devflow>", block + "\n".join(stale) + "\n</devflow>")
    except (OSError, UnicodeError, ValueError, TypeError):
        # This context-only hook must still inject its pointer if a document cannot be read.
        pass
    return DIRECTIVE


def main(event: dict) -> None:
    # Trigger evals opt out explicitly so the session pointer cannot choose the skill for them.
    if os.environ.get("EVAL_DEVFLOW_SKIP_SESSION_START") == "1":
        return
    # Claude Code reads both the top-level and the nested field without deduplicating, so emit
    # exactly one: nested under Claude Code, top-level anywhere else.
    context = directive(event)
    if os.environ.get("CLAUDE_PLUGIN_ROOT") and not os.environ.get("COPILOT_CLI"):
        out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": context}}
    else:
        out = {"additionalContext": context}
    sys.stdout.write(json.dumps(out))
