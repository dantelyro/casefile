# Reviewer

`devflow:reviewer` (`agents/reviewer.md`). The agent that writes a test never proves it can fail; the
reviewer does, by breaking the code in its own worktree (see D-045). What it may edit and run is in
[10-guards.md](10-guards.md).

### REV-001 · The reviewer breaks the line behind each rule's main test      [MANUAL]
Given a change with rule tests, after the reviewer's own re-run
When it reviews each rule's main test
Then it breaks the line that implements the rule, runs that test, quotes the result, and restores the
file with `git restore <file>`.

### REV-002 · The reviewer runs its own breaks and edge cases      [MANUAL]
Given a rule's main test
When the reviewer follows the code path the test covers
Then it also breaks it the ways the implementer had no reason to try — a wrong branch, a missing
filter, a redundant check, a constant off by one — and tries the edge cases the rule names or
implies, running, quoting and restoring each the same way. An edge case the code gets
wrong is a finding against the code, with the input that shows it.

### REV-003 · A break that stays green is a major finding      [MANUAL]
Given a break the reviewer ran
When the test stays green
Then it is a major finding, for any rule, naming the test and the change that slipped past it.

### REV-004 · A break counts as red only on an assertion      [MANUAL]
Given a break the reviewer ran
When the test fails on a crash, a missing name or an import error instead of an assertion
Then the break is not counted as red, and the test is treated as not covering it.

### REV-005 · The worktree is clean before and after the breaks      [MANUAL]
Given the reviewer is about to break code
When `git status --porcelain` is not empty, before the first break or after the last restore
Then it gives no verdict and says what was left.

### REV-006 · The report carries a BREAKS line      [MANUAL]
Given a review of a change with rule tests
When the reviewer replies
Then its block has `BREAKS: <per test: the change → red (the failing assertion) | green>; git
status: clean`.

### REV-007 · The reviewer never commits or writes a test      [MVP]
Given the reviewer found a weak test, an untested edge case or a bug
When it acts on it
Then it reports it as a finding and changes nothing that survives the review: it never commits and
never writes or edits a test (enforced by GUARD-002 and GUARD-003).

### REV-008 · RED: none is accepted only without product code      [MANUAL]
Given a report with `RED: none — <test> passed on first run` (IMPL-002)
When the diff touches product code
Then it is a major finding, as a missing RED is
And when the diff touches only tests, the BREAKS are the proof the tests can fail.

