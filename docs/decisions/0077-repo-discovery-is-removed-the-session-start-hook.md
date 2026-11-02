# D-077 — repo-discovery is removed; the session-start hook warns when the session is outside a git repository

**Status:** Accepted (2026-11-02).
**Decided by:** dantelyro — Grade 1: decided in session on 2026-11-02, in the developer's words quoted above

**Context:** casefile works only inside a git repository: pre_commit, design_check and guard_bash all allow everything when git_root finds none (pre_commit.py:79, design_check.py:97, guard_bash.py:186; read 2026-11-02, Grade 1), and evidence works through git log. repo-discovery's steps were checked one by one: telling a repository from a parent folder of siblings is the only one casefile needs; reading CLAUDE.md is done by Claude Code, reading the decisions by the session-start context, the watermark by evidence, stack and entry points by the model on its own. In a test session in an empty folder (2026-11-02) it did not trigger. Frontend and backend in separate repositories are handled by repo and siblings in casefile.json (D-041).

**Options:** (a) keep repo-discovery; (b) trim it to the overlaps it does not share; (c) remove it and move the repository check into the SessionStart hook.

**Decision:** (c). The developer: 'the point of it is just to find if he is in a folder with sinbling repos or inside a repo but casefile to work properly must be in a repo', then 'put it together with the refactor'. session_start.py puts a <casefile-no-repository> block first when the session's folder is not inside a git repository: the guards and the decision log do not apply, and the session asks the developer which repository to work in.

**Trade-offs:** The check runs every session start, a git call, and never misses, where the skill depended on its description matching. The 138 lines of orientation advice (map before territory, CI as the honest run command, report what could not be determined) are gone; nothing replaces them. A session that cds into another repository later in the session gets no warning, and the guards still miss a 'cd X && git commit' in one command (found 2026-11-02, not yet an issue).
