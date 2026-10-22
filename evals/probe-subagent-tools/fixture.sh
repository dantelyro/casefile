#!/usr/bin/env bash
# Probe: one source file in a git repository, so `git status` has something to say.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src
printf 'export function score() { return 0; }\n' > src/jobs.js
git add -A && git commit -qm init
printf 'untracked\n' > notes.txt
