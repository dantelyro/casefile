# Implementer

`devflow:implementer` (`agents/implementer.md`). It writes the tests and the code for one task or
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
