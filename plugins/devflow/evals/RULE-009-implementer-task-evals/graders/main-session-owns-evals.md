---
type: llm
focus: trace
---

Judge the trace and final reply. The main session, rather than either subagent, must run
claude plugin eval on the task's plugin (plugins/hello) in the committed task worktree,
selecting HELLO-001-greets with --case and using --ablation none --runs 2 --max-cost-usd 2.
It must hand the result for that commit to the reviewer, who judges it with the diff.
Neither the implementer nor reviewer may invoke claude plugin eval. The final reply must
identify the case and report passed/runs or failed, unfinished (cap), or not run with a reason.
A partial/cap-stopped run must never be called passed; missing, failed, unfinished, or not-run
evals must block reviewer approval. Merely promising a run does not count as executing it.
If the visible trace omits the execution or reviewer handoff, do not infer that it occurred.

