# D-014 — A scaffold is planned on disk before any command runs

**Status:** Accepted (2026-08-30).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: chose it from three proposed skill
shapes in session ("the skill will ask all questions first and then write the plan").

**Implemented by:** `19d9e44` — 2026-08-30.

**Context:** A scaffold is roughly twenty commands across one or two repos. Asked one question at a
time and executed as it goes, a wrong answer at question four is discovered at command nineteen,
with a half-built project on disk and no record of what already ran.

**Options:** (a) ask and execute conversationally, phase by phase; (b) ask everything, write
`scaffold.plan.md` naming every command and file, stop for approval, then execute; (c) split the
skill in two — stack scaffolding and design system as separate skills.

**Decision:** (b). (c) was separately adopted for the design system (D-016) but not as the answer to
this question.

**Trade-offs:** One extra approval stop per scaffold, and a file that must be kept in step with what
the skill actually does — a plan that lies is worse than no plan. What it buys: the exact generator
invocations are reviewable *before* anything exists, which is the only way the "never type a
version" rule (D-015) can be checked by a human rather than trusted; and a failed run resumes by
reading a file instead of reconstructing what already happened.

**Consequence:** the plan is not deleted after execution. It stays in the repo as the record of what
was generated and why.
