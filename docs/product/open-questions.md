# Open questions

- Can the reviewer work in the implementer's worktree, one worktree per change instead of per agent
  run? Needs a live probe: whether an agent without `isolation` keeps its shell in another folder
  after `cd`, and whether the `cwd` the hooks see follows it. Blocks nothing yet. Answers: the probe.
