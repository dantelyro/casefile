#!/usr/bin/env bash
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src docs/decisions docs/product
printf 'export function saveJob(job) { return { ...job, saved: true }; }\n' > src/jobs.js
cat > CLAUDE.md <<'EOF'
# Jobs

Read [the architecture](docs/mental-model.md) before changing code.
Decisions are recorded in docs/decisions/.
EOF
cat > docs/mental-model.md <<'EOF'
# Mental model

The app keeps saved jobs. The saveJob function in src/jobs.js returns a copy with saved set to true.
There are no runtime dependencies and no database integration yet.
EOF
cat > docs/decisions/0001-saved-jobs-stay-private.md <<'EOF'
# D-001 · Saved jobs stay private
Date: 2026-09-01
Status: Accepted
Decided by: Ana Souza

## Context
Saved jobs are personal bookmarks.

## Decision
Saved jobs are visible only to their owner.

## Alternatives
A public saved-jobs page was rejected.

## Evidence
The product owner Ana Souza explicitly chose private bookmarks.
EOF
cat > docs/decisions/README.md <<'EOF'
# Decisions

| ID | Decision | Status |
|---|---|---|
| [D-001](0001-saved-jobs-stay-private.md) | Saved jobs stay private | Accepted |
EOF
cat > docs/product/product-decisions.md <<'EOF'
# Product decisions

- Saved jobs are visible only to their owner (2026-09-01), see D-001
- Saved jobs never expire (2026-09-01)
EOF
git add -A
git commit -qm 'chore: seed migration fixture, no new product decisions'
