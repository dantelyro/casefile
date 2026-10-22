---
name: RULE-009-implementer-task-evals
description: Main session owns task eval execution and reviewer handoff
tags: [behaviour]
runs: 2
max_turns: 40
allowed_tools: [Skill, Agent, Read, Glob, Grep, Bash, Edit]
---

Use the devflow:implement skill to build M1 using the existing docs/plans/M1.md plan, which I
approve exactly as written. Follow its task implementation, main-session eval and reviewer flow.
Stop after the reviewer verdict; do not merge. Quote the implementer report, actual task eval
results and reviewer verdict.
The existing app test command is intentional; I decline adding a linter for this fixture.

