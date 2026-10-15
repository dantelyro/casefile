# D-029 — `git push` asks the developer and is denied to every agent

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-14: "you
can change the git push rule to a promt to the developer in my devflow but never to a agent should
do it on it own".
**Implemented by:** `65adde2` — 2026-10-15.

**Context:** Inverso's `block_push.py` denied every push from every session, the developer's
included, so the developer pushed by hand outside Claude Code. The 0.13.0 probe showed that a
PreToolUse `ask` reaches the developer from the main session and from an agent, in auto mode too,
and that a headless run with nobody to answer refuses it.

**Options:** (a) deny every push, as Inverso did; (b) ask in the developer's own session, deny to
every agent; (c) allow in the developer's session, deny to agents.

**Decision:** (b). A push starting any statement — `git -C x push`, after `;`, `&&` or `|`, inside
`{ }`, in PowerShell — asks when `agent_type` is absent and is denied to any agent, with "Commit
locally and report back; the developer reviews and pushes." Text in quotes never counts, so a
commit message mentioning a push does not trigger it.

**Trade-offs:** Every push in the developer's session costs one confirmation. A session started
with `--agent` carries `agent_type` (documented, not probed) and is treated as that agent: its
pushes are denied, not asked.
