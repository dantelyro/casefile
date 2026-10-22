---
name: EVID-001-update-the-docs-to-devflows-format
description: "A request to update docs to devflow's format invokes the evidence skill"
tags: [trigger, EVID-001]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
env:
  EVAL_DEVFLOW_SKIP_SESSION_START: "1"
---

Update the docs to devflow's format.
