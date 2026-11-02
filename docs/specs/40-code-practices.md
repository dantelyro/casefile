# Code practices

The `casefile:code-practices` skill, which the main session and the reviewer follow
when they write or review code, and the Stop hook that runs the project's linter (see D-066, D-067). The
practices are scoped to the stack being changed: a Node change never gets React's rules. The stacks
are Node, React, Vue and Python, with a shared backend file and a shared frontend file.

### PRAC-001 · The skill body holds only stack-independent rules
Given `skills/code-practices/SKILL.md`
When it is checked
Then it is at most 150 lines, so the compaction re-attach (first 5,000 tokens) carries all of it,
and it holds only rules that apply in every stack — naming, readability, function size, comments,
tests — as do/don'ts with a Red flags table.

### PRAC-002 · Only the changed stack's practices load      [MANUAL]
Given code about to be written or reviewed
When the skill chooses which stack files to read
Then it reads them from the nearest manifest of the changed code: a `package.json` depending on
`react` → React and the shared frontend file; on `vue` → Vue and the shared frontend file; any other
`package.json` → Node and the shared backend file; `pyproject.toml`, `requirements*.txt` or
`setup.py` → Python and the shared backend file. Server code inside a React or Vue app also reads
Node and the shared backend file
And it never reads a stack file for code the change does not touch.

### PRAC-003 · Stack files are linked only from the skill body
Given the files under `skills/code-practices/references/`
When they are checked
Then each is linked directly from `SKILL.md`, and none links another reference file.

### PRAC-004 · Practices fit the project's size      [MANUAL]
Given a practice that adds structure — layering, domain-driven design, events, an interface with one
implementation
When the project does not already use it and the developer has not asked for it
Then it is not introduced.

### PRAC-005 · The project's own rules win      [MANUAL]
Given a practice that disagrees with the project's `CLAUDE.md`, its linter configuration or its
design system
When the code is written or reviewed
Then the project's rule is followed.

### PRAC-006 · The session-start pointer names the skill
Given a session starts
When `session_start` emits its context
Then the context asks for `casefile:code-practices` before the session's first change to code, as a
pointer, not the skill's body (D-003).

### PRAC-007 · The reviewer preloads the skill
Given `agents/reviewer.md`
When its frontmatter is read
Then it lists `casefile:code-practices` under `skills`
A live probe on Claude Code 2.1.312 (2026-10-31) showed a plugin agent with only the Read tool
recite a word found only in a skill its `skills` field named as `<plugin>:<skill>` (grade 1).

### PRAC-008 · Reviewer findings cite the practice      [MANUAL]
Given the reviewer finds code that breaks a practice
When it reports the finding
Then the finding cites the practice's rule ID; a security practice or a missing test is a major
finding, any other practice at most minor.

### PRAC-009 · The skill proposes the linter rules, and writes them only after a yes      [MANUAL]
Given an app whose `lint` command is missing from `.claude/casefile.json`, or whose linter config
lacks the stack's measurable rules — names, complexity, nesting depth, function length, magic
numbers
When the skill runs
Then it proposes the stack's rule set for the project's own linter, and writes nothing before the
developer's yes.

### PRAC-010 · The Stop hook lints what changed during the turn
Given the main session ends a turn, and an app in `.claude/casefile.json` has a `lint` command
When that app's files changed during the turn — compared with their state when the previous turn
ended, or when the session started for its first turn
Then the hook runs that app's `lint`, and on failure blocks the end of the turn with the lint
output as the reason
And an app whose files did not change during the turn is not linted, even with changes from before.

### PRAC-011 · The Stop hook does not block a retry
Given the turn is already continuing because of a Stop hook (`stop_hook_active`)
When the hook runs
Then it does not block again
The field is documented in the hooks reference (grade 3); the developer confirms it in a live run
when the milestone finishes.

### PRAC-012 · The Stop hook never blocks without something to lint
Given no `.claude/casefile.json`, no app with `lint`, no change during the turn, or a `lint` that
times out or cannot start
When the hook runs
Then it does not block; a timeout or a start failure is reported to the developer as a
`systemMessage`, because the hooks reference gives a Stop hook no field that reaches the session
without continuing the turn. A Stop hook cannot fail closed: `onFailure` has no effect on Stop events.
