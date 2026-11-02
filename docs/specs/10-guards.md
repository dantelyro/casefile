# Guards

What `hooks/casefile_hooks/guard_bash.py` refuses or asks about, and how every hook fails. The rules
apply alike to the main session and to any agent (see D-074). Rules here cover what changed since
0.20.0; the rest is in `history/2026-10-14-review-design.md`, "Guard rules", where GUARD-009
overrides anything that design gives an agent alone. GUARD-004, 006 and 008, the planner's and the
implementer's rules, were removed with them (D-074); the reviewer keeps its own.

### GUARD-001 · The reviewer edits only inside the repository it works in
Given `casefile:reviewer` writes a file with Edit, Write, MultiEdit or NotebookEdit
When the file lies inside the repository of the reviewer's working folder (`cwd`): the developer's
checkout, where it reviews
Then the write is allowed, subject to GUARD-002
And outside that repository, or when git cannot tell, it is denied. See D-045 and D-072.

### GUARD-002 · The reviewer never edits tests, records or settings
Given `casefile:reviewer` writes a file
When the file is a test file (`TEST_FILE` in `pre_commit.py`), under a `.claude` folder, under
`docs/issues/`, under the plans or specs folders, or under a `protected_paths` entry
Then the write is denied. The reviewer breaks product code; it does not change tests or records.

### GUARD-003 · The reviewer may restore files with git restore
Given `casefile:reviewer` runs a command
When the whole command is one `git restore` statement whose every word is one of the flags `-p`,
`--patch`, `-q`, `--quiet`, `--`, or a path of plain characters (letters, digits,
`. _ - / @ +`, and spaces only inside quotes), with at least one path
Then it is allowed
And any other `git restore` is denied — no path, any other flag (`--staged`, `-S`, `--source`, `-s`
and their abbreviations among them), a git option before `restore`, or any other character — as are
`git add`, `commit`, `stash`, `checkout`, `switch`, `reset`, file-changing shell and redirects into files: the
reviewer works in the developer's checkout and never moves it (D-072).

### GUARD-005 · The reviewer restores only inside the repository it works in
Given `casefile:reviewer` runs a `git restore` that GUARD-003 allows
When its working folder (`cwd`) is outside any repository, or git cannot tell
Then it is denied; in the developer's checkout, where it reviews, it is allowed. See
D-045 and D-072.

### GUARD-007 · A hook registered as never-blocks never blocks
Given a hook whose command in `hooks/hooks.json` ends with `never-blocks` (one that only adds context)
When it cannot be found, its input cannot be read, it crashes, or no Python 3.10+ is found
Then it prints nothing and exits 0; without Python, a `SessionStart` event instead gets the message
asking Claude to tell the developer how to install it
And every other hook is a guard: the same failures deny the call. Whether a hook may block is
declared only in `hooks/hooks.json`, never by its name in the starter or the launcher.

### GUARD-009 · An agent gets no rules of its own
Given a tool call from an agent — casefile's, a built-in one such as `Explore`, or another plugin's
When the guards check it
Then it is allowed, denied or asked about exactly as the same call from the main session would be, except for the
reviewer's own rules (GUARD-001, 002, 003, 005): no other rule reads `agent_id` or `agent_type`, and `git push` asks the developer from either (see D-074).
