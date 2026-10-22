#!/usr/bin/env bash
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src
printf 'export function saveJob(job) { return job; }\n' > src/jobs.js
git add -A
git commit -qm init
