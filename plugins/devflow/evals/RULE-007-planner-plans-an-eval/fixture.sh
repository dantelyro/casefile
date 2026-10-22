#!/usr/bin/env bash
# A tiny plugin project: one skill rule and one script rule in milestone M1, no plan yet.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p plugins/devflow/.claude-plugin plugins/devflow/skills/greet plugins/devflow/scripts .claude docs/specs docs/plans docs/product
printf '{"name": "devflow", "version": "0.1.0", "description": "Greets"}\n' > plugins/devflow/.claude-plugin/plugin.json
printf -- '---\nname: greet\ndescription: Greets the user. Use when the user says hello.\n---\n\nAnswer the greeting in Portuguese.\n' > plugins/devflow/skills/greet/SKILL.md
printf 'def main():\n    print("")\n\n\nif __name__ == "__main__":\n    main()\n' > plugins/devflow/scripts/greet.py
printf '{"build_order": "docs/product/blueprint.md"}\n' > .claude/devflow.json
cat > docs/specs/README.md <<'EOF'
# Specs

| File | Covers |
| --- | --- |
| [10-greet.md](10-greet.md) | The greet skill and its script |
EOF
cat > docs/specs/10-greet.md <<'EOF'
# Greet

### GREET-001 · The greet skill answers in Portuguese
Given a user who says hello
When the greet skill runs
Then the reply is in Portuguese.

### GREET-002 · greet.py prints the name it is given
Given `greet.py` run with the argument `Ana`
When it finishes
Then it prints `Ana` and exits 0.

### GREET-003 · The greeting feels warm      [MANUAL]
Given a user who says hello
When the greet skill answers
Then the developer judges the reply feels warm, not curt.
EOF
cat > docs/product/blueprint.md <<'EOF'
# Blueprint

## Build order
1. M1 Greeting: GREET-001, GREET-002, GREET-003
EOF

git add -A && git commit -qm init
