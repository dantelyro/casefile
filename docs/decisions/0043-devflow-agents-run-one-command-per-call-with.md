# D-043 — Devflow agents run one command per call, with a timeout, and never wait in a loop

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: asked for in session on 2026-10-19.

**Context:** On devflow 0.16.1 an implementer ran typecheck, lint, e2e and the commit as one chained command, each step piped into tail. It did not return; the agent waited about 30 minutes in sleep and until loops until the developer stopped it, with no report, and tail hid which step hung. Run separately with timeout in the same worktree, the steps took 6 s, 4 s and 14 s. A rule in agent prose alone is one the agent can stop following (skill-authoring.md, [CC]).

**Options:** (a) prose in the implementer and reviewer only; (b) prose plus a hook that refuses, for devflow agents, a command with ;, &&, ||, several lines or | tail, and sleep of 10 s or more and until/while loops.

**Decision:** (b), the developer's call: chained commands are prohibited, in the hook. Quoted text does not count, and other pipes (git log | head) still pass. The main session and other agents are not restricted.

**Trade-offs:** An agent that needs two steps spends two calls; cd dir && cmd has to become two calls or a path argument. A legitimate while-read loop is refused too.
