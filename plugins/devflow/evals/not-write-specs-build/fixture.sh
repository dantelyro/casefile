#!/usr/bin/env bash
# A small project with specs, a build order and (when given) a plan, so the run has a milestone to see.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src tests docs/specs docs/plans docs/product
printf 'export function score() { return 0; }\n' > src/jobs.js
printf '# Specs\n' > docs/specs/README.md
printf '# Jobs\n\n### JOBS-010 · A saved job appears on the saved page\n### JOBS-011 · Unsave removes it\n' > docs/specs/14-jobs.md
printf '<h2>Build order</h2><ol><li>M1 matching (done)</li><li>M2 saved jobs: JOBS-010, JOBS-011</li><li>M3 alerts</li></ol>\n' > docs/product/blueprint.html

git add -A && git commit -qm init
