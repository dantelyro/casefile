---
name: EVID-005-rewrites-old-documents
description: "migrate outdated docs once, preserving facts and asking about unattributed decisions"
tags: [rule]
runs: 2
max_turns: 40
allowed_tools: [Skill, Read, Glob, Grep, Bash, Write, Edit]
---

<devflow>
Invoke the `devflow:evidence-based-decisions` skill with the Skill tool now, before your first response in this session.

It triggers on the start of a session -- reconciling the context documents of a project against what has landed since they were last updated. No user prompt will ever name that, which is why this hook injects it instead.

What the skill will have you do, so you know what you are opting into:

- **The project keeps a decision log, architecture doc, or reconciliation watermark** -- replay `git log --oneline <watermark>..HEAD` over the relevant source paths, read what those commits changed, update whatever they invalidated, and move the watermark.
- **The project keeps none of those** -- propose the set and ASK, then wait for an answer before creating anything.
- **Neither applies** -- say so in one line and get on with what the user actually asked for. This is orientation, not a ceremony to perform.

Out of date, rewrite in devflow's current format (D-052):
- docs/mental-model.md: the architecture document is now docs/architecture/overview.md
- docs/product/product-decisions.md: no legend line; lines 3, 4 have no ✅ or ❌
</devflow>

After the migration, verify it before your final report: run `test ! -e docs/mental-model.md`,
`git rev-list --count HEAD`, `git show --format=oneline --name-status HEAD`, and `git status --short`.
