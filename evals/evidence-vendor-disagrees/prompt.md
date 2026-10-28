---
name: evidence-vendor-disagrees
description: "evidence must fire"
tags: [trigger]
runs: 2
max_turns: 8
allowed_tools: [Skill, Read, Glob, Grep]
---

The payment provider's docs say the refund endpoint returns 200 with a refund_id field, but in production we get 202 with an id field. Which one should our client code trust?
