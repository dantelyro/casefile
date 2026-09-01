# D-021 — The frontend actor drafts the design direction

**Status:** Accepted (2026-08-31).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session.

**Implemented by:** `56b69f8` — 2026-08-31.

**Context:** The dev team's `frontend` actor owns flows, states and the component set, and a brief
about any of those runs straight into typography, spacing and colour — the ground D-016 already
carved off into its own skill, on the reasoning that the design-system phase needed a browser, an
interaction round-trip and a rendering surface no day-zero skill can offer. Building `frontend`'s
prompt meant deciding, again, how close to that boundary the actor gets to stand.

**Options:** (a) let `frontend` render or choose an actual palette and theme as part of its round;
(b) absorb the design-system skill into `mvp` so one skill owns the question end to end;
(c) `frontend` drafts the design direction in text only — tokens, component set, and the theme
seams D-016 already named — and stops there.

**Decision:** (c). D-016 stands: (a) was rejected because a colour palette produced in a blind text
round is a palette nobody has seen, which is exactly the unfalsifiable output D-016 already ruled
out once. (b) was considered and refused for the same two reasons D-016 gave and that have not
changed — the work needs a browser and an interaction round-trip to get a choice back out of a
rendered page, and it is most useful on a project that already exists, neither of which a skill
that runs before anything is built can offer. `frontend` instead writes the brief a design system
would render: the tokens, the component set, and the named seams — `shared/theme/tokens.scss`,
Mantine's CSS variables, `quasar.variables.scss`, `tailwind.config` — so the second skill has
something to start from instead of nothing.

**Trade-offs:** A project seeded by `mvp` still looks like stock Mantine, stock Quasar or bare Radix
until the design-system skill runs, same as D-016 already accepted. What `frontend` adds is a
written direction instead of a blank theme file — closer to a real starting point, but still not a
seen one, and the gap between the two is exactly the gap D-016 drew the line at.
