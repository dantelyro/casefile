# D-054 — The shipped plugin lives in plugins/devflow; development stays at the root

**Status:** Accepted (2026-10-22).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-22, "great do it", on the layout proposed in the session (plugin under plugins/devflow, development at the root) after `claude plugin eval` refused the root plugin over .venv's hard links.

**Context:** D-002 hoisted the plugin to the repository root. uv hard-links 515 files into .venv/, and claude plugin eval refuses a plugin folder holding a hard link, so no eval could run with the plugin at the root (M4 T1). It also refuses an eval dir outside the plugin root (--eval-dir must stay inside the plugin root (no ..)), so evals cannot stay outside a nested plugin.

**What D-002 got wrong:** D-002 hoisted the plugin to the root for update behaviour (commit 42d8300, "feat: auto-update"); that link is its own reconstruction's inference. Anthropic's "Host and maintain a marketplace" page (https://code.claude.com/docs/en/plugins/host-marketplace) says a user gets a new copy when the plugin's version changes, through background auto-update (off by default for a third-party marketplace) or `/plugin marketplace update`, and draws no distinction between a root and a nested relative source. So a nested `source` should still update. Grade 3 (documentation prose), not observed here. D-002 also did not foresee that a root plugin holds `.venv/`'s hard links.

**Options:** (a) keep the root as the plugin and run evals from a git archive export each time; (b) move the shipped files to plugins/devflow/, keep tests, docs, pyproject.toml and uv.lock at the root, and put evals/ inside the plugin.

**Decision:** (b). marketplace.json stays at the root with source ./plugins/devflow; plugins/devflow/ holds .claude-plugin/plugin.json, agents/, hooks/, skills/, shared/ and evals/. Only it ships. Supersedes D-002.

**Trade-offs:** Two layers to navigate, and every path in tests, CI and docs gained a prefix. In exchange evals run on a worktree directly and the shipped plugin holds nothing that is development-only. D-002's open question about a second plugin is answered: it sits beside devflow in plugins/.
