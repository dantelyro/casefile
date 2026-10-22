---
name: EVID-002-specs-request-goes-to-write-specs
description: "A feature-spec request invokes write-specs rather than the evidence skill"
tags: [trigger, EVID-002]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
env:
  EVAL_DEVFLOW_SKIP_SESSION_START: "1"
---

Write the specs for a new feature: users can save a job, see their saved jobs on one page, and unsave one.
