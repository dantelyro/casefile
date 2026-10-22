# D-054 — The shipped plugin lives in plugins/devflow; development stays at the root

**Status:** Accepted (2026-10-22).
**Decided by:** dantelyro (2026-10-22: great do it)

**Context:** D-002 hoisted the plugin to the repository root. uv hard-links 515 files into .venv/, and claude plugin eval refuses a plugin folder holding a hard link, so no eval could run with the plugin at the root (M4 T1). It also refuses an eval dir outside the plugin root (--eval-dir must stay inside the plugin root (no ..)), so evals cannot stay outside a nested plugin.

**Options:** (a) keep the root as the plugin and run evals from a git archive export each time; (b) move the shipped files to plugins/devflow/, keep tests, docs, pyproject.toml and uv.lock at the root, and put evals/ inside the plugin.

**Decision:** (b). marketplace.json stays at the root with source ./plugins/devflow; plugins/devflow/ holds .claude-plugin/plugin.json, agents/, hooks/, skills/, shared/ and evals/. Only it ships. Supersedes D-002.

**Trade-offs:** Two layers to navigate, and every path in tests, CI and docs gained a prefix. In exchange evals run on a worktree directly and the shipped plugin holds nothing that is development-only. D-002's open question about a second plugin is answered: it sits beside devflow in plugins/.
