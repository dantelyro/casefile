"""SessionStart: the project context and the evidence pointer for the main session.

The main session starts with CONTEXT, where the project's decisions and product documents are and
what to do with them, followed by DIRECTIVE, the pointer to the evidence skill (CTX-002). No agent
is given either: casefile's one agent, the reviewer, reads the decisions itself (D-074).

The evidence skill triggers on "the start of a session", which no user prompt ever says, so the
skill never fires on its own judgement; this injects the trigger (D-003). It injects a pointer,
not the skill body, so the per-session cost stays at a few hundred tokens (D-004). The pointer
waits for the first change to code or docs, so a session that only asks questions pays nothing
more (D-057), or for the first decision, which is recorded even when no file changes (D-064).
"""

import json
import sys

CONTEXT = """<casefile-context>
This project may record why it is the way it is. Before you act on code, specs or plans, read what applies to your work: the decision index (`docs/decisions/README.md`, or where the project's `CLAUDE.md` says) and, in full, every decision whose subject or cited rules touch the files or rules you work on; `docs/product/product-decisions.md` and `docs/product/open-questions.md` when the work concerns the product. A document the project does not have is absent; never invent one.

A decision marked superseded, and work recorded as dropped or reverted, is not brought back. When your work would contradict an accepted decision or revive dropped work, do not build around it: say so, naming the decision.
</casefile-context>"""

DIRECTIVE = """<casefile>
Before you change any code or document in this session, invoke the `casefile:evidence` skill with the Skill tool. A session that only asks questions, explains or plans does not need it.

Invoke it too, unasked, the moment a decision is settled in this session, even if no file changes: the developer picks between options, or work is dropped, reverted or reversed. The skill records it in the project's decision log; without the record, the reason lives only in this conversation.

It reconciles the context documents of a project against what has landed since they were last updated. No user prompt will ever ask for that, which is why this hook injects it instead.

What the skill will have you do, so you know what you are opting into:

- **The project keeps a decision log, architecture doc, or reconciliation watermark** -- run `git log --oneline <watermark>..HEAD` over the relevant source paths, read what changed, update whatever it invalidated, and move the watermark.
- **The project keeps none of those** -- propose the set and ASK, then wait for an answer before creating anything.
- **Neither applies** -- say so in one line and get on with what the user actually asked for. This is orientation, not a ceremony to perform.
</casefile>"""


def main(event: dict) -> None:
    text = CONTEXT + "\n\n" + DIRECTIVE
    # Claude Code reads both the top-level and the nested field without deduplicating, so emit
    # exactly one: the nested form.
    sys.stdout.write(json.dumps({"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": text}}))
