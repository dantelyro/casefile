"""SessionStart: point Claude at the evidence skill.

evidence-based-decisions triggers on "the start of a session", which no user prompt ever says, so
the skill never fires on its own judgement; this injects the trigger (D-003). It injects a pointer,
not the skill body, so the per-session cost stays at a few hundred tokens (D-004).
"""

import json
import os
import sys

DIRECTIVE = """<devflow>
Invoke the `devflow:evidence-based-decisions` skill with the Skill tool now, before your first response in this session.

It triggers on the start of a session -- reconciling the context documents of a project against what has landed since they were last updated. No user prompt will ever name that, which is why this hook injects it instead.

What the skill will have you do, so you know what you are opting into:

- **The project keeps a decision log, architecture doc, or reconciliation watermark** -- replay `git log --oneline <watermark>..HEAD` over the relevant source paths, read what those commits changed, update whatever they invalidated, and move the watermark.
- **The project keeps none of those** -- propose the set and ASK, then wait for an answer before creating anything.
- **Neither applies** -- say so in one line and get on with what the user actually asked for. This is orientation, not a ceremony to perform.
</devflow>"""


def main(event: dict) -> None:
    # Claude Code reads both the top-level and the nested field without deduplicating, so emit
    # exactly one: nested under Claude Code, top-level anywhere else.
    if os.environ.get("CLAUDE_PLUGIN_ROOT") and not os.environ.get("COPILOT_CLI"):
        out = {"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": DIRECTIVE}}
    else:
        out = {"additionalContext": DIRECTIVE}
    sys.stdout.write(json.dumps(out))
