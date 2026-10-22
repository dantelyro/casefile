#!/usr/bin/env bash
# A tiny skill plugin with one task eval. Shell-enabled: run on Fedora, not native Windows.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p .claude docs/specs docs/product docs/plans plugins/hello/.claude-plugin plugins/hello/skills/hello plugins/hello/evals/HELLO-001-greets/graders
printf 'plugins/hello/evals/results/\n.claude/worktrees/\n' > .gitignore
cat > .claude/devflow.json <<'EOF'
{"default_branch":"main","build_order":"docs/product/blueprint.md","apps":{"app":{"path":".","test":"python -c \"pass\"","install":"python -c \"pass\""}}}
EOF
printf '{"worktree":{"baseRef":"head"}}\n' > .claude/settings.json
printf '{"name":"hello","description":"A greeting skill for an eval fixture","version":"0.1.0"}\n' > plugins/hello/.claude-plugin/plugin.json
cat > plugins/hello/skills/hello/SKILL.md <<'EOF'
---
name: hello
description: Greets a user asking for a greeting.
---
Reply with exactly Hello.
EOF
cat > plugins/hello/evals/HELLO-001-greets/case.yaml <<'EOF'
schema_version: "1.1"
name: HELLO-001-greets
EOF
cat > plugins/hello/evals/HELLO-001-greets/prompt.md <<'EOF'
---
name: HELLO-001-greets
description: Portuguese greeting
runs: 2
max_turns: 4
allowed_tools: [Skill]
---
Use the hello skill to greet me.
EOF
cat > plugins/hello/evals/HELLO-001-greets/graders/greeting.md <<'EOF'
---
type: regex
target: last_message
pattern: 'Olá'
---
EOF
cat > docs/specs/README.md <<'EOF'
# Specs

## Files

| File | What |
|---|---|
| [10-hello.md](10-hello.md) | Greeting |
EOF
cat > docs/specs/10-hello.md <<'EOF'
# Greeting

### HELLO-001 · Greet in Portuguese

Given a user asking for a greeting
When the hello skill replies
Then its reply is exactly Olá.
EOF
printf '# Hello\n\n## Build order\n\n- **M1 — Greeting** (0.2.0): HELLO-001.\n' > docs/product/blueprint.md
cat > docs/plans/M1.md <<'EOF'
# Plan: M1 Greeting
Planned: 2026-10-22

Scope: M1 — Greeting: HELLO-001.

## Tasks
### T1 · Greet in Portuguese
- Status: todo
- Rules: HELLO-001
- App: app
- Test first: plugins/hello/evals/HELLO-001-greets/
- Then implement: plugins/hello/skills/hello/SKILL.md
- Done when: the task eval scores 2/2, and python -c "pass" exits 0
- Depends on: none
- Parallel-safe with: none
- Notes: This is skill prose, not code. Change Hello to Olá and commit; the main session runs the eval after the commit and hands its results to the reviewer. Agents must not invoke claude plugin eval.

## Rules covered
- HELLO-001 → T1
EOF
git add -A
git commit -qm init
git switch -q -c t1
printf '%s\n' '---' 'name: hello' 'description: Greets a user asking for a greeting.' '---' 'Reply with exactly Olá.' > plugins/hello/skills/hello/SKILL.md
git add -A
git commit -qm 'feat: greet in Portuguese [HELLO-001]'
git switch -q main

