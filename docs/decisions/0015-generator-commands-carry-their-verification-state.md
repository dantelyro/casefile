# D-015 — Generator commands carry their verification state

**Status:** Accepted (2026-08-30).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: stated the rule the skill exists to
enforce ("i dont want is package version manually built. always run npm command as much as
possible").

**Implemented by:** `19d9e44` — 2026-08-30.

**Context:** The skill's premise is that generators, not memory, produce projects. But the
*commands* are themselves written from memory, and CLIs rename flags, add prompts and change
defaults between minor versions. A generator command written from documentation is exactly what
`evidence-based-decisions` grades as a hypothesis — prose about a system, not an observation of it.

There is a second, sharper failure: a generator that stops on a prompt hangs the session outright.
There is no interactive terminal to answer it.

**Options:** (a) record the commands as fact and fix them when they break; (b) mark each command
`VERIFIED <date>` / `UNVERIFIED` / `INTERACTIVE` in `references/generators.md`, and surface that
state in the plan; (c) verify every command before shipping the skill.

**Decision:** (b). Every command ships `UNVERIFIED` until someone runs it and dates it.

**Trade-offs:** (c) is strictly better evidence and was not done — verifying nine generators across
two ecosystems is a session of its own, and shipping the skill with honest labels beats delaying it
for labels nobody has to trust. The cost is that the first real scaffold is also the verification
pass, and the user is the one who finds the broken flag. The labels are what make that recoverable
rather than mysterious.

**Consequence:** `npm init quasar@latest` is marked `INTERACTIVE` with its answer sequence recorded,
because it is the command most likely to hang a session.
