---
name: evidence-record-why
description: "evidence must fire"
tags: [trigger]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
---

We chose Postgres advisory locks over Redis for the job queue, because we already run Postgres and the queue is small. Write that down so nobody undoes it later.
