#!/usr/bin/env bash
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src docs/specs docs/product .claude
printf 'export function saveJob(job) { return job; }\n' > src/jobs.js
printf '{"build_order":"docs/product/blueprint.md"}\n' > .claude/devflow.json
cat > docs/specs/README.md <<'EOF'
# Specs

| File | What |
|---|---|
| [14-jobs.md](14-jobs.md) | Saved jobs |
EOF
cat > docs/specs/14-jobs.md <<'EOF'
# Jobs

### JOBS-010 · A saved job appears on the saved page
Given a job
When the user saves it
Then it appears on the saved page
EOF
printf '# Jobs app\n\n## Build order\n\n- **M1 — Saved jobs**: JOBS-010.\n' > docs/product/blueprint.md
git add -A
git commit -qm init
