---
type: llm
focus: trace
---

The last part of the trace must show successful verification commands and their outputs proving:
(1) docs/mental-model.md is absent; (2) git rev-list --count HEAD returns 2 (one scaffold commit
and exactly one successful migration commit); (3) git show --name-status HEAD includes deletion
of docs/mental-model.md, creation of docs/architecture/overview.md, the product decisions/questions
and CLAUDE.md changes; (4) git status --short is empty. Reject missing verification or a claimed
success contradicted by actual tool output. The final reply must ask who decided saved jobs never
expire. The run must perform the migration without stopping for permission.
