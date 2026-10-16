#!/usr/bin/env bash
# A small project with a plan task, a spec, an issue, and a branch for each change to review.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src tests docs/plans docs/specs docs/issues
printf 'export function score(job) { return 0; }\n' > src/jobs.js
printf '# M2\n\n### T3 · Save a job [JOBS-010]\n- Status: in-progress\n' > docs/plans/M2.md
printf '# Jobs\n\n### JOBS-010 · A saved job appears on the saved page     [MVP]\n' > docs/specs/14-jobs.md
printf '# I-0007 — Upload times out\n\n- Status: in-progress\n' > docs/issues/0007-upload-timeout.md
git add -A && git commit -qm init
for b in m2-t3 fix/0007 feat/saved-jobs; do
  git switch -q -c "$b" main
  printf '// %s\n' "$b" >> src/jobs.js
  git commit -qam "work on $b"
done
git switch -q main
