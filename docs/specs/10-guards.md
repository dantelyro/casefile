# Guards

What `hooks/casefile_hooks/guard_paths.py` and `guard_bash.py` let each casefile agent do. Rules here
cover only what changed in 0.20.0; the rest is in `history/2026-10-14-review-design.md`, "Guard
rules".

### GUARD-001 · The reviewer edits only inside its own worktree
Given `casefile:reviewer` writes a file with Edit, Write, MultiEdit or NotebookEdit
When the file lies in a linked worktree (its git dir differs from its common dir), and it is the same
worktree as the reviewer's working folder (`cwd`)
Then the write is allowed, subject to GUARD-002
And in the main checkout, in any other linked worktree (an implementer's, another reviewer's), outside
any repository, or when git cannot tell, it is denied, the reason saying breaks happen only in the
reviewer's own worktree. See D-045.

### GUARD-002 · The reviewer never edits tests, records or settings
Given `casefile:reviewer` writes a file inside a linked worktree
When the file is a test file (`TEST_FILE` in `pre_commit.py`), under a `.claude` folder, under
`docs/issues/`, under the plans or specs folders, or under a `protected_paths` entry
Then the write is denied. The reviewer breaks product code; it does not change tests or records.

### GUARD-003 · The reviewer may restore files with git restore
Given `casefile:reviewer` runs a command
When the whole command is one `git restore` statement whose every word is one of the flags `-W`,
`--worktree`, `-p`, `--patch`, `-q`, `--quiet`, `--`, or a path of plain characters (letters, digits,
`. _ - / @ +`, and spaces only inside quotes), with at least one path
Then it is allowed
And any other `git restore` is denied — no path, any other flag (`--staged`, `-S`, `--source`, `-s`
and their abbreviations among them), a git option before `restore`, or any other character — as are
`git add`, `commit`, `stash`, `checkout`, `reset`, file-changing shell and redirects into files.

### GUARD-004 · The planner stays read-only
Given `casefile:planner` runs a command
When it is `git restore`
Then it is denied, as every other repository-changing command is.

### GUARD-005 · The reviewer restores only in its own worktree
Given `casefile:reviewer` runs a `git restore` that GUARD-003 allows
When its working folder (`cwd`) is not a linked worktree: the main checkout, outside any repository,
or git cannot tell
Then it is denied, the reason saying breaks happen only in the reviewer's own worktree. See D-045.

### GUARD-006 · The implementer never edits specs or plans
Given `casefile:implementer` writes a file with Edit, Write, MultiEdit or NotebookEdit
When the file is under the specs folder (`specs_dir`) or the plans folder (`plans_dir`), whether or
not `protected_paths` lists them
Then the write is denied, the reason saying to report `STATUS: blocked` with the question: a wrong or
silent spec, and every change to a plan, are the developer's to rule on.

### GUARD-007 · A hook registered as never-blocks never blocks
Given a hook whose command in `hooks/hooks.json` ends with `never-blocks` (one that only adds context)
When it cannot be found, its input cannot be read, it crashes, or no Python 3.10+ is found
Then it prints nothing and exits 0; without Python, a `SessionStart` event instead gets the message
asking Claude to tell the developer how to install it
And every other hook is a guard: the same failures deny the call. Whether a hook may block is
declared only in `hooks/hooks.json`, never by its name in the starter or the launcher.
