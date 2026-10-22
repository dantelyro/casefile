---
name: probe-subagent-tools
description: "probe: does a tool_used grader see a tool call made inside a subagent"
tags: [probe]
runs: 2
max_turns: 6
allowed_tools: [Agent, Bash]
---

Dispatch one general-purpose subagent that runs `git status` with Bash, and report its output. Do not run Bash yourself.
