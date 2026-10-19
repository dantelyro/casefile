# D-041 — Sibling repositories hold the same specs and plan, and each builds its own tasks

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: asked for in session on 2026-10-19.

**Context:** Frontend and backend in separate repositories (PetTool, devflow 0.16.1): each repository grew its own build order and its own docs/plans/M0.md, the backend plan held tasks for both, and the frontend planner had to read ../pettool-backend to see what was done. Reported in a review of devflow by another developer. An agent's worktree is always created in the repository the session runs in, so one session cannot build a sibling's task.

**Options:** (a) specs in one repository, the other points to them; (b) the same specs, milestone and plan in every repository, every session writing statuses into both copies; (c) the same specs, milestone and plan in every repository, written into the sibling only when they are created, each task's Repo: naming its builder, and each repository reading the sibling's copy for the status of tasks it does not build.

**Decision:** (c), the developer's call: specs, milestones and plan are completely the same in both, each task points at its part; each repository checks its sibling for what is completed, and a spec that involves the sibling is written there too, so a session opened there continues without brainstorming again. Decision entries stay numbered per repository. Reading a sibling relies on permissions.additionalDirectories, which is documented but not yet seen on a live two-repository session (Grade 3).

**Trade-offs:** A sibling's status lines in the local copy go stale and are ignored. Writing into a sibling needs it on its default branch with a clean tree. Supersedes, for siblings only, write-specs working only in the repository it runs in (5a12d9d).
