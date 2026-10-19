# Lint and test tooling

ruff and pytest, run through uv, adopted in their own milestone after M3. How the suite moves to
pytest, how today's ruff findings are handled and where the tools are installed from are open
questions; every rule here stays `[LATER]` until they are answered.

### TOOL-001 · The code passes ruff      [LATER]
Given the repository's Python code
When ruff checks it through uv
Then it exits 0.

### TOOL-002 · Lint runs before every commit      [LATER]
Given `.claude/devflow.json`
When a commit touches the repository
Then the `devflow` app's `lint` command runs ruff, and pre_commit refuses the commit on a finding.

### TOOL-003 · The suite runs under pytest      [LATER]
Given the test suite
When pytest runs it through uv
Then it collects and passes every test.

### TOOL-004 · Hooks stay standard library      [LATER]
Given the code under `hooks/`
When ruff and pytest are adopted
Then it imports nothing outside the standard library (D-027).
