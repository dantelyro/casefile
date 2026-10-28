#!/usr/bin/env bash
# A small project that keeps a decision log and a watermark, with one commit landed after it.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p src docs/decisions
printf 'export function run(args) { return args.length; }\n' > src/cli.js
printf '# D-001 — Payments go through the provider SDK\n\n**Status:** Accepted (2026-09-01).\n' > docs/decisions/0001-payments-go-through-the-provider-sdk.md
printf '# Decisions\n\n| ID | Decision | Status |\n|---|---|---|\n| [D-001](0001-payments-go-through-the-provider-sdk.md) | Payments go through the provider SDK | Accepted |\n' > docs/decisions/README.md
git add -A && git commit -qm "feat: cli and payments"
WM=$(git rev-parse --short HEAD)
printf '# shop\n\n**Docs reconciled through:** `%s` — 2026-09-01\n\nA small shop CLI. Decisions live in `docs/decisions/`.\n' "$WM" > CLAUDE.md
git add -A && git commit -qm "docs: project instructions"
printf 'export function run(args) { return args.filter(Boolean).length; }\n' > src/cli.js
git add -A && git commit -qm "fix: ignore empty arguments"
