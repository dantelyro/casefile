---
name: EVID-001-reconcile-the-docs
description: "A request to reconcile docs invokes the evidence skill"
tags: [trigger, EVID-001]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
env:
  EVAL_DEVFLOW_SKIP_SESSION_START: "1"
---

Reconcile the docs.
