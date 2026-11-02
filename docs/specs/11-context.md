# Project context

What the main session is told about the project's documents when it starts
(`hooks/casefile_hooks/session_start.py`). No agent is given casefile's context (see D-074); CTX-001,
which gave it to every agent (D-070), was removed with the agents.

### CTX-002 · The main session starts with the project context and its behaviour
Given a session starts, is cleared or is compacted
When the session-start hook runs
Then its one context field holds the project context — where the decision index and product
documents are, to read in full every decision touching its work, that superseded or dropped work is
not brought back, and that it says so instead of building around a contradiction — followed by the
pointer to the evidence skill.
