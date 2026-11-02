---
name: fix-bug
description: >
  Use first — before reading or editing any code — when the developer asks to fix a bug or an
  issue, or when a bug needs recording as an issue in docs/issues/. The main session reproduces the
  bug with a failing test first, fixes it on a fix/ branch, commits it once after the developer says
  yes, and leaves the branch for the developer to merge. Triggers on: "fix docs/issues/0007",
  "there's a bug: … fix it", "the upload fails when …, can you fix it", a bug found while building a
  feature. Not for a typo or one-line
  change the developer asks to make directly, and not for explaining an error without fixing it.
---

# Fix a bug

A bug is fixed **on its own `fix/` branch, never inside a feature's**, and proven by a test that
failed before the fix. You write the test and the fix yourself, with no agent (ORCH-017, D-074).
The developer merges the branch; you never do.

## The issue

Every bug is a file in `docs/issues/`, whoever found it. `docs/issues/` is created the first time
an issue is filed, only after the developer agrees to it.

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

- `Status` is `open`, `in-progress`, `fixed` (set in the fix's own commit, ORCH-013) or `wontfix: <reason>`.
- `Blocks` names the plan task that cannot proceed until this is fixed: a bug in accepted work the
  task builds on. That task waits until the developer has merged the fix into the milestone's branch.
- A bug in the change under review is not an issue: it is a review finding for that change.
- The test is named in backticks, its file first. The status script looks for that name.

## Steps

1. **The issue.** Use the file the developer points to, or write it now from their report — what
   happens, what should happen, how to see it, the test that must fail first — and show it before
   saving.
2. **The branch.** Create the `fix/` branch following
   [`${CLAUDE_PLUGIN_ROOT}/shared/work-branch.md`](../../shared/work-branch.md). Commit the issue on
   it (`docs(issues): I-0007 <title>`), with `in-progress`.
3. **Fix** following [`${CLAUDE_PLUGIN_ROOT}/shared/build-task.md`](../../shared/build-task.md): the
   issue's test first, failing on an assertion through the code the bug is in, then the least fix that
   makes it pass. Report to the developer as that file says.
4. **Commit once** (ORCH-003), after the developer's yes: the issue becomes `- Status: fixed`, then
   `git add -A`, and one commit holds the test, the fix and the status: `fix(<scope>): <what> [I-0007]`.
5. **Check.** Run `issues_status.py` (as in *The issue*) and show the developer its result; a fixed
   issue it reports as an error is not fixed. Then tell them the branch is ready to merge, and that
   `review` can check it first if they want.

## Never

- Never fix a bug inside a feature branch, or a feature inside a bug branch.
- Never mark an issue fixed before its test failed, then passed, and the developer said yes.
- Never merge the `fix/` branch: the developer does.
