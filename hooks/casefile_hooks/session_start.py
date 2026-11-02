"""SessionStart: the project context, the evidence pointer and the code guidelines for the main session.

The main session starts with CONTEXT, where the project's decisions and product documents are and
what to do with them, followed by DIRECTIVE, the pointer to the evidence skill (CTX-002), then
GUIDELINES, the code rules. No agent is given any of them: casefile's one agent, the reviewer,
reads the decisions itself (D-074).

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
- **Always be aware of project stucture** -- the overview.md contains the cleanest project data where you can easly find reusable code, configurations, use-cases, types and more.
</casefile>"""


GUIDELINES = """<casefile-guidelines>
# Code guidelines

Apply these to every line of code you write or change.

## Workflow
- Never guess. Before coding, settle every open question the code depends on: check facts against
  current sources (the code, its docs, a live run), not memory, and ask the developer the rest.
- Before writing something new, look for existing code that does it and reuse it.
- When code does not fit the change, do not work around it: propose the refactor and ask before
  doing it.
- Change only what was asked, one concern per change: no fixes nobody needs, no cleanups or
  renames mixed in. A bug or problem found along the way is reported to the developer and left
  as it is.

## Principles
- Solve the problem in front of you. No speculative abstractions, flags or layers.
- Match the surrounding code: its idiom, structure and comment density.
- Comments say why, not what. Leave code health no worse than you found it.
- Prefer deep modules: a small interface over substantial behaviour; no pass-through wrappers.
- Validate and parse input once at the boundary; inside, use types that cannot hold invalid states.
- Keep libraries that reach outside the program (payment, storage, email, HTTP, database) behind
  your own interface; use small utilities such as lodash or uuid directly.

## Naming and values
- Never use single-letter names (variables, parameters, loop variables, `as` targets, lambdas)
  or abbreviations a newcomer cannot expand: `for invoice in invoices`, `config` not `cfg`.
- No magic numbers or strings. Give every literal with a meaning a named constant:
  `MAX_RETRIES = 3`. Only 0, 1 and -1 as plain arithmetic, and empty values, stay inline.
- Names use the domain's words and reveal intent: `overdue_invoices`, not `list2` or `inv_arr`.
- Numbers with a unit carry it in the name: `TIMEOUT_MS`, `price_cents`, `size_bytes`.
- Booleans read as yes/no questions (`is_active`, `has_access`) and are never negative.
- Functions are verbs that say what they do; a `get` has no side effects.
- One word per concept across the codebase: pick `fetch`, `get` or `load` and keep it.

## Security
- Authorize on the server for every request, deny by default. Parameterize every query.
  No secrets in code or logs. Fail closed on errors.

## Testing
- Build new behaviour test-first: a failing test, the code that passes it, then refactor.
- On a bug: run the tests, gather evidence, reproduce it with a failing test, then fix.
- A test must fail when the code it covers is broken. Test behaviour through public interfaces.
- Existing tests record business rules: never change or delete one to make code pass. Ask the
  developer before changing or deleting any test, saying which rule changed.
- Tests are deterministic and isolated: no sleeps, control time and randomness, no shared state,
  and no dependence on run order.
- Mock only at boundaries you own.
</casefile-guidelines>"""


def main(event: dict) -> None:
    text = f"{CONTEXT}\n\n{DIRECTIVE}\n\n{GUIDELINES}"
    # Claude Code reads both the top-level and the nested field without deduplicating, so emit
    # exactly one: the nested form.
    sys.stdout.write(json.dumps({"hookSpecificOutput": {
                     "hookEventName": "SessionStart", "additionalContext": text}}))
