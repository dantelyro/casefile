# D-064 — Decisions are recorded unasked, including ones with no change and dropped work

**Status:** Accepted (2026-10-29).
**Decided by:** dantelyro — Grade 1: asked for in session on 2026-10-29

**Context:** Recording a decision depended on a change to commit it with and on the evidence skill being loaded. A choice settled in conversation had no commit; a session of questions never loaded the skill; dropping M6 on 2026-10-29 deleted its entry and kept the reason only in a commit message (D-063). The developer: 'all of em should be done automatically fix it'.

**Options:** (a) a spinner tip reminding the developer to ask; (b) the skill and the session-start pointer make recording unasked, name the cases that slipped, and say to record when unsure; (c) a hook that blocks a commit without an entry.

**Decision:** (b). The session-start pointer also asks for the evidence skill the moment a decision is settled, even with no file change; step 4 of the skill records unasked, in the change's commit or one of its own, and when unsure records it; decision-log.md's What earns an entry adds the developer's answer to options put to them, and dropped, reverted or reversed work, whose entries are superseded, never deleted. A project with no decision log still gets the log proposed and waits for a yes: casefile writes no document a project has not agreed to.

**Trade-offs:** Still prose the model may not follow every time; (c) was rejected because a hook cannot tell a decision from an ordinary commit. More entries, some small. The pointer adds about sixty words to every session.
