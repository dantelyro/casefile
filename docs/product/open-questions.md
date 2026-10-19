# Open questions

- Can the reviewer work in the implementer's worktree, one worktree per change instead of per agent
  run? Needs a live probe: whether an agent without `isolation` keeps its shell in another folder
  after `cd`, and whether the `cwd` the hooks see follows it. Blocks nothing yet. Answers: the probe.
- What is the docs reconciliation skill called: `docs-reconciliation`, or shorter (`migrate-docs`)?
  Blocks DOCS-008. Answers: the developer.
- Does it also cover devflow's own check of `docs/skill-authoring.md` against the CLI version, or only
  the layout? Blocks DOCS-001. Answers: the developer.
- Does pytest only run the existing unittest tests, or are they rewritten in pytest's style (which
  supersedes D-027 for `tests/`)? Blocks TOOL-003. Answers: the developer.
- Are all of ruff's findings fixed (51 with ruff 0.17.1's defaults on 2026-10-19), or does a config
  select the rules? Blocks TOOL-001. Answers: the developer.
- Do ruff and pytest run as pinned `uvx` tools, or as dev dependencies in a `pyproject.toml` with a uv
  venv? Blocks TOOL-001, TOOL-002, TOOL-003. Answers: the developer.
