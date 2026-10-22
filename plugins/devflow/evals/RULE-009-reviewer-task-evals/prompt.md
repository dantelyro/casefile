---
name: RULE-009-reviewer-task-evals
description: Main session owns task eval execution and reviewer handoff
tags: [behaviour]
runs: 2
max_turns: 40
allowed_tools: [Skill, Agent, Read, Glob, Grep, Bash]
---

Use the devflow:review skill to review docs/plans/M1.md T1, committed on branch t1. Follow the
skill's main-session task-eval handoff before dispatching the reviewer. Stop after its verdict;
do not merge. Quote the actual task eval results, its TESTS RE-RUN line and verdict.
The existing app test command is intentional; I decline adding a linter for this fixture.

