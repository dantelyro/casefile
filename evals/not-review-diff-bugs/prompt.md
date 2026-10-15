---
name: not-review-diff-bugs
description: "review must not fire: no plan, issue or spec to judge against"
tags: [trigger]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
---

Look over my current uncommitted changes for bugs.
