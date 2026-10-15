---
name: not-review-readability
description: "review must not fire: no plan, issue or spec to judge against"
tags: [trigger]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
---

Can you skim src/utils.ts and tell me if anything reads badly?
