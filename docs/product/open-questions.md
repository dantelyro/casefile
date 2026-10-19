# Open questions

- Can the reviewer work in the implementer's worktree, one worktree per change instead of per agent
  run? Needs a live probe: whether an agent without `isolation` keeps its shell in another folder
  after `cd`, and whether the `cwd` the hooks see follows it. Blocks nothing yet. Answers: the probe.
- What is the docs reconciliation skill called: `docs-reconciliation`, or shorter (`migrate-docs`)?
  Blocks DOCS-008. Answers: the developer.
- Does it also cover devflow's own check of `docs/skill-authoring.md` against the CLI version, or only
  the layout? Blocks DOCS-001. Answers: the developer.
