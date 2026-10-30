---
name: fix-bug
description: >
  Use first — before reading or editing any code — when the developer asks to fix a bug or an
  issue, or when a bug needs recording as an issue in docs/issues/. The bug is reproduced with a
  failing test first, fixed on a fix/ branch by the casefile:implementer agent, reviewed by
  casefile:reviewer, and left for the developer to merge. Triggers on: "fix
  docs/issues/0007", "there's a bug: … fix it", "the upload fails when …, can you fix it", a bug an
  agent reported in its NOTES, a bug found while building a feature. Not for a typo or one-line
  change the developer asks to make directly, and not for explaining an error without fixing it.
---

# Fix a bug

A bug is fixed **on its own `fix/` branch, never inside a feature's**, and proven by a test that
failed before the fix. The main session coordinates; it does not write the fix or the test itself.
The developer merges the branch; you never do.

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
   it (`docs(issues): I-0007 <title>`), with `in-progress`, and note the commit as the fix's base
   (`git rev-parse HEAD`).
3. **Implement.** Dispatch `casefile:implementer` with the issue path only, **without a worktree**:
   it works in this checkout, on the `fix/` branch. Nobody edits or switches branches here until it
   reports. It writes the failing test, confirms it fails for the right reason, fixes, and commits.
4. **Review.** Dispatch `casefile:reviewer` with the issue path, `BASE: <the fix's base>` and the
   implementer's report verbatim. The reviewer works in its own worktree, because it breaks code on
   purpose.
5. **Fix loop.** `changes-requested` → send the blocker and major findings to **the same**
   implementer (continue it), to fix in a new commit and report again. At most 2 rounds; then stop
   and show the developer the findings — the commits stay on the branch for them to keep or drop.
6. **Record** after the reviewer approves and the developer says yes: the issue becomes
   `- Status: fixed (<implementer commit>)`, with unfixed minor findings under "Accepted at merge",
   committed as `docs(issues): I-0007 fixed`.
7. **Check.** Run `issues_status.py` (as in *The issue*) and show the developer its result; a fixed
   issue it reports as an error is not fixed. Then tell them the branch is ready to merge.

## Never

- Never fix a bug inside a feature branch, or a feature inside a bug branch.
- Never write the test or the fix in the main session: a second, isolated implementer and an
  isolated reviewer are the point.
- Never mark an issue fixed before the reviewer approved and the developer said yes.
- Never merge the `fix/` branch: the developer does.
