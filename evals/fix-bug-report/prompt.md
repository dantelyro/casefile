---
name: fix-bug-report
description: "fix-bug must fire"
tags: [trigger]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
---

There's a bug: when a CV has two pages, only the first page's skills are counted. Fix it properly.
