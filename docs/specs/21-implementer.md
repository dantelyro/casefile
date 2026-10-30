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

### IMPL-004 · The implementer checks its task against the decision log      [MANUAL]
Given a task or an issue
When the implementer starts it
Then it reads the decisions index and in full every accepted decision touching the files it will
change or the rules it builds
And a task that would contradict one, or bring back something dropped, reverted or superseded, is
reported `STATUS: blocked`, naming the decision, instead of built. See D-065.
