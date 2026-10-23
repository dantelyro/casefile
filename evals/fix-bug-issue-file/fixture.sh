#!/usr/bin/env bash
# A small Node project with one open issue, so the run has real code to look at.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src tests docs/issues
cat > package.json <<'J'
{ "name": "uploads", "private": true, "scripts": { "test": "node --test" } }
J
cat > src/upload.js <<'J'
export function pagesToRead(cv) { return cv.pages.slice(0, 1); }
J
cat > tests/upload.test.js <<'J'
import { test } from "node:test";
J
cat > docs/issues/0007-upload-timeout.md <<'J'
# I-0007 — Upload times out on CVs over 2 MB

- Status: open
- Found: reported by the developer
- Blocks: none
- Related to: none
- Rules: CV-004

## What happens
Uploading a 3 MB PDF times out after 30 s.
## What should happen
Files up to 10 MB upload within 10 s.
## How to see it
Upload fixtures/cv-3mb.pdf.
## Test that must fail first
`tests/upload.test.js` — `CV-004: a 3 MB CV uploads`
J
git add -A
git commit -qm init
