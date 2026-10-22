#!/usr/bin/env bash
# A small project with code, specs (README with its file table, one area file) and a Markdown build order.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src tests docs/specs docs/product
printf 'export function saveJob(job) { return job; }\n' > src/jobs.js
cat > docs/specs/README.md <<'EOF'
# Specs

The ID is the area's prefix and a three-digit number. A rule needs no tag. Tags: `[LATER]`, `[VERIFY]`, `[MANUAL]`.

## Files

| File | What |
|---|---|
| [14-jobs.md](14-jobs.md) | Saved jobs |
EOF
cat > docs/specs/14-jobs.md <<'EOF'
# Jobs

### JOBS-010 · A saved job appears on the saved page

```
Given a job
When the user saves it
Then it appears on the saved page
```
EOF
cat > docs/product/blueprint.md <<'EOF'
# Jobs app

## Build order

- **M1 — Saved jobs** (0.1.0): JOBS-010.
EOF
mkdir -p .claude
printf '{\n  "build_order": "docs/product/blueprint.md",\n  "default_branch": "main"\n}\n' > .claude/devflow.json

git add -A && git commit -qm init
