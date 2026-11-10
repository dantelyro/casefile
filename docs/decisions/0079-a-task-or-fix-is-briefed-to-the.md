# D-079 — A task or fix is briefed to the developer in plain words before it is built, and waits for their go

**Status:** Accepted (2026-11-10).
**Decided by:** the developer — Grade 1: asked in session on 2026-11-10, in their words quoted above

**Context:** build-task told the session to report after building, not before. While building a long milestone the developer asked to be told before each task what it does and why, because they do not remember what the plan agreed, and said 'i really love this way of working with you briefing me on every task ... i wanna make this part of every workflow from now on'. They also asked, more than once, that a question be answered before any tool runs.

**Options:** (a) leave it to each project's memory or CLAUDE.md; (b) a step in shared/build-task.md, so implement and fix-bug both brief before building; (c) a line in the session-start code guidelines, for every session.

**Decision:** (b), the developer asked to change the skill: 'go to casefile folder under personal and make a change to the skill and add this behavior'. build-task gets a 'Brief, then wait' step between reading and red: what the task does and why, the rules, what changes for the user, the files, and what existing or legacy code does that the task or specs leave out, with a proposal for each; then the developer's go, task by task. Its Rules add that a developer's question is answered in words before any tool runs, and that a question or an unclear reply is not a go. The developer then added a rule of their own: a plain yes is not accepted when more than one question is open; the open questions are listed and the developer is asked which one the yes answers.

**Trade-offs:** One more round-trip per task: a milestone of thirty tasks waits on thirty more replies. The answer-first rule applies to every session but lives only in build-task, so write-specs, review and evidence sessions do not get it unless it moves to the guidelines later.
