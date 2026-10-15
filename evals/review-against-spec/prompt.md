---
name: review-against-spec
description: "review must fire"
tags: [trigger]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
---

Check the implementer's work on feat/saved-jobs: does it meet the rules in docs/specs/14-jobs.md, and do its tests actually test them?
