# Guards

What `hooks/devflow_hooks/guard_paths.py` and `guard_bash.py` let each devflow agent do. Rules here
cover only what changed in 0.20.0; the rest is in `history/2026-10-14-review-design.md`, "Guard
rules".

### GUARD-001 · The reviewer edits only inside its own worktree      [MVP]
Given `devflow:reviewer` writes a file with Edit, Write, MultiEdit or NotebookEdit
When the file lies in a linked worktree (its git dir differs from its common dir), and it is the same
worktree as the reviewer's working folder (`cwd`)
Then the write is allowed, subject to GUARD-002
And in the main checkout, in any other linked worktree (an implementer's, another reviewer's), outside
any repository, or when git cannot tell, it is denied, the reason saying breaks happen only in the
reviewer's own worktree. See D-045.

### GUARD-002 · The reviewer never edits tests, records or settings      [MVP]
Given `devflow:reviewer` writes a file inside a linked worktree
When the file is a test file (`TEST_FILE` in `pre_commit.py`), under a `.claude` folder, under
`docs/issues/`, under the plans or specs folders, or under a `protected_paths` entry
Then the write is denied. The reviewer breaks product code; it does not change tests or records.

### GUARD-003 · The reviewer may restore files with git restore      [MVP]
Given `devflow:reviewer` runs a command
When the whole command is one `git restore` statement whose every word is one of the flags `-W`,
`--worktree`, `-p`, `--patch`, `-q`, `--quiet`, `--`, or a path of plain characters (letters, digits,
`. _ - / @ +`, and spaces only inside quotes), with at least one path
Then it is allowed
And any other `git restore` is denied — no path, any other flag (`--staged`, `-S`, `--source`, `-s`
and their abbreviations among them), a git option before `restore`, or any other character — as are
`git add`, `commit`, `stash`, `checkout`, `reset`, file-changing shell and redirects into files.

### GUARD-004 · The planner stays read-only      [MVP]
Given `devflow:planner` runs a command
When it is `git restore`
Then it is denied, as every other repository-changing command is.

### GUARD-005 · The reviewer restores only in its own worktree      [MVP]
Given `devflow:reviewer` runs a `git restore` that GUARD-003 allows
When its working folder (`cwd`) is not a linked worktree: the main checkout, outside any repository,
or git cannot tell
Then it is denied, the reason saying breaks happen only in the reviewer's own worktree. See D-045.
