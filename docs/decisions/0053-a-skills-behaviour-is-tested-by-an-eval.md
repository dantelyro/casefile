# D-053 — A skill's behaviour is tested by an eval, and MANUAL marks what the developer approves

**Status:** Accepted (2026-10-21).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-21, in the developer's words quoted under Context, then 'automatically with a $2 cap'.

**Context:** RULE-003 (D-049) tagged every agent or skill rule [MANUAL] because 'the AI has no way to test it'. claude plugin eval runs the skill on a real model with graders over the files a run wrote, its final reply, its tool calls, or an llm judge (code.claude.com/docs/en/plugin-evals). The developer: 'yeah pytest cant run a model but you can', and 'manual are for also critical thing that the dev should also test and give his ok'. Past runs in evals/results/ estimated about $0.09-0.16 per run at list price; on a subscription that is plan usage, not a charge.

**Options:** Who runs evals: (a) automatically, the implementer and the reviewer, under a cap; (b) only when the developer starts them. Cap: $2 or $5 per invocation, or ask each time.

**Decision:** A rule describing a skill's or agent's behaviour gets an eval at evals/<RULE-ID>-<slug>/, counted by rules_coverage as its test (RULE-007, RULE-008). [MANUAL] marks what nothing can run, or a rule the developer marks critical, which keeps its eval; a milestone is done only after the developer's ok on each (RULE-003). The implementer and the reviewer run a task's evals with --ablation none --runs 2 --max-cost-usd 2; commits and CI do not (RULE-009). Existing [MANUAL] rules keep their tag until the rule itself is next changed.

**Trade-offs:** Evals are nondeterministic and use plan usage or API spend; two runs per agent per task is the floor that still smooths randomness. A run the cap stops is unfinished, not passed. CLAUDE.md's 'billed, so on demand' no longer holds for task evals. (b) leaves skill rules unchecked until someone remembers.
