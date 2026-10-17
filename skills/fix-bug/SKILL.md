---
name: fix-bug
description: >
  Use first — before reading or editing any code — when the developer asks to fix a bug or an
  issue, or when a bug needs recording as an issue in docs/issues/. The bug is reproduced with a
  failing test first, fixed on its own branch by the devflow:implementer agent, reviewed by
  devflow:reviewer, and merged after the developer says yes. Triggers on: "fix
  docs/issues/0007", "there's a bug: … fix it", "the upload fails when …, can you fix it", a bug an
  agent reported in its NOTES, a bug found while building a feature. Not for a typo or one-line
  change the developer asks to make directly, and not for explaining an error without fixing it.
---

# Fix a bug

A bug is fixed **on its own branch, never inside a feature's**, and proven by a test that failed
before the fix. The main session coordinates; it does not write the fix or the test itself.

## The issue

Every bug is a file in `docs/issues/`, whoever found it. `docs/issues/` is created the first time
an issue is filed, only after the developer agrees to it. Agents never write issues (the hooks
refuse it): they report bugs in their `NOTES`, and the main session files them once the developer
says yes.

Get the id and file prefix from the script, never by counting by hand:
`<python> "${CLAUDE_PLUGIN_ROOT}/skills/fix-bug/scripts/issues_status.py" --next-id`, where
`<python>` is `py -3` on Windows and `python3` elsewhere.

```
# I-0007 — Web image fails to build with nested test files

- Status: open
- Found: 2026-10-14, during docs/plans/M1.md T11      (or: reported by the developer)
- Blocks: docs/plans/M1.md T13                         (or: none)
- Related to: docs/plans/M1.md T8                      (the work it was found in, or: none)
- Rules: ARCH-001

## What happens
## What should happen
## How to see it
## Test that must fail first
`web/tests/image.test.ts` — `ARCH-001: nested test files stay out of the image`
```

- `Status` is `open`, `in-progress`, `fixed (<implementer commit>)` or `wontfix: <reason>`.
- `Blocks` names the plan task that cannot proceed until this is fixed: a bug in merged work the
  task builds on. That task waits; the fix is merged first.
- A bug inside a task's own unmerged branch is not an issue: it is a review finding for that task.
- The test is named in backticks, its file first. The status script looks for that name.

## Steps

1. **The issue.** Use the file the developer points to, or write it now from their report — what
   happens, what should happen, how to see it, the test that must fail first — and show it before
   saving. Commit it on the default branch (`docs(issues): I-0007 <title>`), and set `in-progress`.
2. **Implement.** The project settings must be in place first, as in `implement`'s preconditions:
   without `worktree.baseRef: "head"` the implementer starts without the issue you just committed.
   Then dispatch `devflow:implementer` with the issue path only. It writes the failing
   test, confirms it fails for the right reason, fixes, and commits on its own branch.
3. **Review.** Dispatch `devflow:reviewer` with the issue path and the implementer's report
   verbatim.
4. **Fix loop.** `changes-requested` → send the blocker and major findings to **the same**
   implementer (continue it, so it keeps its worktree), to fix in a new commit and report again.
   At most 2 rounds; then stop and show the developer the findings.
5. **Merge** after the developer's yes, following
   [`${CLAUDE_PLUGIN_ROOT}/shared/merge.md`](../../shared/merge.md). The issue becomes
   `fixed (<implementer commit>)` in the merge commit.
6. **Check.** Run `issues_status.py` (as in *The issue*) and show the developer its result; a fixed
   issue it reports as an error is not fixed.

## Never

- Never fix a bug inside a feature branch, or a feature inside a bug branch.
- Never write the test or the fix in the main session: a second, isolated implementer and an
  isolated reviewer are the point.
- Never mark an issue fixed on a branch that was not merged.
- Never merge without the developer's yes for this change.
