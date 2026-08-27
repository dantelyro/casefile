# D-005 — Hook scripts are extensionless, behind a cmd/bash polyglot wrapper

> **Reconstructed entry (2026-08-27).** Read from the author's comment block in
> `hooks/run-hook.cmd`, which states the Windows auto-detection behaviour and the extensionless
> naming rule. The failure that prompted it is **not** recorded anywhere in the repo, so
> "otherwise the hook does not run on Windows" is inference from the workaround's shape.

**Status:** Accepted (2026-08-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `2a2476b`, the `feat`
commit that added `hooks/run-hook.cmd`.
**Implemented by:** `2a2476b` — 2026-08-19.

**Context:** The hook from D-003 has to run on Windows, where this plugin is developed, as well
as on Unix. Two behaviours constrain it: Claude Code's Windows path prepends `bash` to any hook
command containing `.sh`, and `cmd.exe` cannot run a shell script at all.

**Options:** (a) ship a `.sh` and rely on the `.sh` auto-detection to invoke bash;
(b) ship separate `.cmd` and `.sh` implementations and keep them in step by hand;
(c) one file that is valid in both interpreters — `: << 'CMDBLOCK'` opens a heredoc under bash
that swallows the batch section, while `cmd.exe` never reaches the shell lines below — dispatching
to extensionless script files so the `.sh` auto-detection never engages.

**Decision:** (c). `run-hook.cmd` searches the two standard Git for Windows locations, then
`bash` on `PATH`, and execs the named script. Hook scripts are named `session-start`, not
`session-start.sh`. When no bash is found it exits 0 silently.

**Trade-offs:** The wrapper is unreadable at a glance and order-sensitive — anything above the
first line breaks both interpreters — so it carries more comment than code. Silent exit 0 means a
genuinely broken hook looks exactly like a machine without bash: the plugin degrades quietly to
no context injection rather than failing loudly. That was the right trade for optional context
and would be the wrong one for anything load-bearing.
