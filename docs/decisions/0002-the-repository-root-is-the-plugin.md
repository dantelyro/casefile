# D-002 — The repository root is the plugin

> **Reconstructed entry (2026-08-27).** The move and its shape are read from `42d8300`; the
> commit subject is `feat: auto-update`, which names the goal but not the reasoning. The
> connection between root placement and update behaviour is **inferred** from the diff and the
> README. To be confirmed.

**Status:** Superseded by D-054 (accepted 2026-08-07).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `42d8300`, the `feat`
commit that moved the manifest and retargeted `source`.
**Implemented by:** `42d8300` — 2026-08-07.

**Context:** The repo started as a marketplace with the plugin nested at `plugins/devflow/`,
its `marketplace.json` entry pointing at `./plugins/devflow`. This is the arrangement that
scales to several plugins, and it was the layout for the first three commits.

**Options:** (a) keep the nested layout and accept whatever update behaviour it produced;
(b) hoist the single plugin to the root, so `marketplace.json` points its one entry at `./` and
both manifests sit side by side in one `.claude-plugin/` folder.

**Decision:** (b). `plugin.json` moved from `plugins/devflow/.claude-plugin/` to
`.claude-plugin/`, beside `marketplace.json`, and `source` became `"./"`.

**Trade-offs:** The root is now occupied. A second plugin cannot follow the same pattern — it
needs `plugins/<name>/.claude-plugin/plugin.json` and its own `marketplace.json` entry, so the
repo would hold two different layouts at once. Accepted on the basis that one plugin is the
current reality and the asymmetry is documented rather than discovered.

**The open question this exposes, deliberately not decided here:** whether a second plugin should
trigger a move back to a uniform nested layout, or live alongside the root plugin as an
exception.
