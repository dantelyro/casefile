# I-0001 — plan_status misses planner choices written as sub-bullets of Notes

- Status: open
- Found: 2026-10-19, by the M2 planner (docs/plans/M2.md), after none of M1's planner choices showed
- Blocks: none
- Related to: docs/plans/M1.md
- Rules: none

## What happens
`skills/implement/scripts/plan_status.py` reads `Planner choice:` only from the text on the `- Notes:`
line itself (line 66). A plan whose Notes are indented sub-bullets under `- Notes:` — the layout of
docs/plans/M1.md, which the planner wrote — reports no `choices`, so `implement` step 1 shows the
developer no planner choice to accept or cut (D-044). The M2 planner worked around it by writing each
task's Notes as one long line.

## What should happen
Every `Planner choice:` inside a task's Notes is reported, whether it is on the `- Notes:` line or on
the indented lines under it, until the next field or task.

## How to see it
`py -3 skills/implement/scripts/plan_status.py docs/plans/M1.md` lists no `planner choice:` lines,
though `grep -c "Planner choice" docs/plans/M1.md` finds 10.

## Test that must fail first
`tests/test_plan_status.py` — `test_choices_in_indented_notes_are_reported`
