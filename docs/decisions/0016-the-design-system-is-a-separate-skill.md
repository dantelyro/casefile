# D-016 — The design system is a separate skill

**Status:** Accepted (2026-08-30).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session ("i think will will
drop the design system for this skill and build another one").

**Implemented by:** pending.

**Context:** The original scope included a phase that asked for typography, spacing and colour in
the browser, rendered against templates — login, dashboard, profile, lists, buttons, cards — and
wrote the answers into the project's theme file. Getting a *choice* back out of a browser page needs
a channel: a local server, or a published Artifact the user edits and the session re-reads.

**Options:** (a) keep the phase in `scaffolding`, using the superpowers brainstorming companion's
local server; (b) keep it, using an Artifact; (c) drop it from `scaffolding` and make it its own
skill later.

**Decision:** (c). (a) was ruled out independently and permanently — "i dont want cross skill
dependency" — because it would make this plugin depend on another plugin's script path inside its
cache directory.

**Trade-offs:** A project scaffolded today looks like stock Mantine, stock Quasar, or bare Radix
until the second skill exists. Against that: the design phase was the only part of the skill needing
a browser, an interaction round-trip and a rendering surface, and it was carrying most of the
delivery risk. It is also the part that is *useful on an existing project*, which a day-zero-only
skill cannot be — so separating it makes it better, not merely smaller.

**Consequence:** each component branch's theme seam is named in `references/frontend-react.md` and
`frontend-vue.md` — `shared/theme/tokens.scss`, Mantine's CSS variables, `quasar.variables.scss`,
or `tailwind.config`. Those are the addresses the second skill writes to.
