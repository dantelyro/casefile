# Implementer

`casefile:implementer` (`agents/implementer.md`). It writes the tests and the code for one task or
issue; it no longer proves its own tests can fail (see D-045).

### IMPL-001 · The implementer runs no breaks      [MANUAL]
Given a task or an issue
When the implementer works through it
Then it has no break-check step, and its report has no BREAKS line; the breaks are the reviewer's
(REV-001).

### IMPL-002 · Behaviour that already exists reports RED: none      [MANUAL]
Given a task whose behaviour already exists in the code
When its tests pass on the first run
Then the report says `RED: none — <test> passed on first run`, and the implementer touches no product
code.

### IMPL-003 · The implementer uses what the task says to reuse      [MANUAL]
Given a task with a `Reuse:` line (PLAN-004)
When the implementer builds it
Then it uses the code named there, and anything it does not use goes under NOT DONE with the reason.

### IMPL-004 · A task that contradicts a decision is reported blocked      [MANUAL]
Given a task or an issue, with the project context every agent starts with (CTX-001)
When it would contradict an accepted decision touching the files it changes or the rules it builds,
or bring back something dropped, reverted or superseded
Then the implementer reports `STATUS: blocked`, naming the decision, and builds nothing. See D-065.
