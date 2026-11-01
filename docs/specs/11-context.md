# Project context

What every session and every agent is told about the project's documents when it starts
(`hooks/casefile_hooks/session_start.py`). The reading is delivered by a hook so that no prompt has
to repeat it; what a role does with what it read stays in that role's rules (see D-070).

### CTX-001 · Every agent starts with the project context
Given any agent is spawned — casefile's own, a built-in one such as `Explore`, or another plugin's
When it starts
Then its context holds the project context: where the decision index and product documents are, to
read in full every decision touching its work, that superseded or dropped work is not brought back,
and that it reports a contradiction instead of building around it
And it never holds the main session's behaviour: invoking the evidence skill, reconciling the docs,
recording decisions.

### CTX-002 · The main session starts with the project context and its behaviour
Given a session starts, is cleared or is compacted
When the session-start hook runs
Then its one context field holds the project context of CTX-001 followed by the pointer to the
evidence skill.
