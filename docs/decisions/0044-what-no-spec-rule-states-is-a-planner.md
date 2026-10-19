# D-044 — What no spec rule states is a planner choice the developer accepts or cuts

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: asked for in session on 2026-10-19.

**Context:** On devflow 0.16.1 a spec asked only for a different password. The planner added an overlap rule: the wrong password was a second account's real password. Generated fixtures repeat their sequence in every test process, so the second account sometimes had the same password, and the test passed only by run order. It cost a review round and a long explanation to the developer, who fixed it with a derived password.

**Options:** (a) the planner rule against invented requirements, as it stood; (b) every note no spec rule states starts with Planner choice:, plan_status.py lists them, and the developer accepts or cuts each one when approving the plan.

**Decision:** (b), the developer's call. A cut choice leaves the task's Notes; an accepted one stays part of the task.

**Trade-offs:** The approval step gets longer on plans with many choices. A choice the planner fails to mark still reads as part of the task; the reviewer's spec-match check is what catches it.
