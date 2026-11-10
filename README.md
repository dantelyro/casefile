# casefile

A [Claude Code](https://claude.com/claude-code) plugin that makes Claude work from your project's
record instead of from its own guesses: why the code is the way it is, what the product must do,
what was tried and dropped. It adds five skills, one reviewer agent, and a set of guards that hold
the rules that must never be broken.

## Why

Claude does not remember your project from one session to the next. Without a written record to
read, this is what goes wrong:

- **It brings back what you dropped.** It rebuilds something you removed last month, or quietly
  contradicts a choice you made, because the reason lived only in an old conversation.
  casefile writes each decision down with its reasons, and Claude reads the ones touching its work
  before it changes anything. Dropped work stays dropped until you say otherwise.
- **It invents requirements.** It builds from a vague request and fills the gaps itself.
  With casefile a feature becomes numbered spec rules first, and what nobody decided stays an open
  question for you.
- **Its tests agree with its code.** It writes the code, then tests that match it, and reports
  "done". With casefile every rule gets a test that must fail before the code exists, each task is
  explained to you before it is built, and it is committed only after your yes.
- **It calls a mock a working integration.** With casefile, a claim about a system you do not
  control carries an evidence grade, and "built" is reported apart from "verified against the real
  system".
- **It approves its own work.** It reviews a change by the same reasoning that wrote it.
  casefile's reviewer is a separate agent that did not write the change: it checks it against the
  spec, re-runs the tests, and breaks the code to prove the tests can fail.
- **It forgets an instruction mid-session.** It skips a failing test, pushes, or wipes a database
  volume. In casefile those rules are hooks, not instructions: they run on every command and
  refuse it.

## Install

**You need** Python 3.10 or newer, and on Windows [Git for Windows](https://gitforwindows.org):
Claude Code runs casefile's hooks through its Git Bash. If Python is missing, casefile says so at the
start of the session and asks before installing it; until then its guards refuse commands and file
edits.

```
/plugin marketplace add dantelyro/casefile
/plugin install casefile@dantelyro
```

Then turn auto-update on: `/plugin` → **Marketplaces** → `dantelyro` → **Enable auto-update**.
Claude Code leaves it off for marketplaces that are not Anthropic's own, so without this step you
stay on the version you installed. To update by hand, run `/plugin marketplace update dantelyro`.
A new version loads on the next launch, or with `/reload-plugins`.

## What changes once it is installed

Nothing is written into your project until you agree to it. Two things happen on their own.

**Every session starts with casefile's context.** A few hundred tokens that tell Claude where your
decisions and product documents are, to read the ones that touch its work, and never to bring back
dropped work; then a short set of code guidelines (naming, tests first, no guessing, change only
what was asked). A session that only asks questions pays nothing more. In a project that keeps a
decision log or an architecture document, Claude checks, before its first change, what was
committed since those documents were last updated, and brings them up to date.

**The guards are on.** They apply to your session and to every agent, and they fail closed: when a
guard cannot run, the action is refused, not let through.

| When Claude tries to | casefile |
| --- | --- |
| `git push` | asks you first, every time |
| `docker compose down -v` | refuses: it deletes your database volumes |
| commit with `--no-verify` | refuses: fix what the hook reports |
| commit a skipped or focused test (`it.skip`, `it.only`, `@pytest.mark.skip`…) | refuses |
| commit a change to an app whose tests or lint fail | refuses, and shows the last lines of the output (once you have set the app's commands, see [Settings](#settings)) |
| write UI code with a colour, spacing or font your design system does not define | refuses, and tells Claude to ask you to extend the design system (once you have set it up, see [Settings](#settings)) |

Outside a git repository none of this applies, and Claude is told so at the start of the session.

## How you work with it

You talk to Claude as usual. Each skill starts when you ask for what it does.

```
an idea ──► write-specs ──► implement ──► (review) ──► you merge
a bug ────► fix-bug ──────────────────► (review) ──► you merge
```

| You say | Skill | What happens |
| --- | --- | --- |
| "write the specs for saved jobs", "turn this brainstorm into specs" | `write-specs` | Claude drafts numbered rules, a milestone, and the decisions and open questions it found in what you said. It shows the draft, asks every open question at once, and writes only after your yes. |
| "build M2", "continue the milestone" | `implement` | Claude plans the milestone as small tasks tied to rule IDs and waits for your approval. Then, for one task at a time: it tells you what the task does, waits for your go, writes the failing tests, writes the code, reports, and commits once after your yes. |
| "there's a bug: the upload fails when…, fix it" | `fix-bug` | The bug is written down as an issue, reproduced with a test that fails, then fixed, on its own branch. |
| "review this branch before I merge" | `review` | The `casefile:reviewer` agent checks the change against its task and the spec rules, runs the tests itself, and answers approve or changes-requested with findings. It runs only when you ask. |
| nothing: it starts on its own | `evidence` | Keeps the decision log and the project documents true, and records a decision the moment you make one. |

### Specs: rules with IDs

A spec rule is a small statement of behaviour with an ID that never changes:

```
### MATCH-003 · Required skills weigh 70%
Given a job with required and nice-to-have skills
When the score is computed
Then required skills contribute 70 of the 100 points
```

The ID links a test to the business rule it proves, and the rule to where it came from. A test is
named after its rule (`MATCH-003: …`), so it is never a test of plain code: it fails when that rule
is broken, and anyone reading it can open the rule. The rule in turn cites the decision behind it
(`see D-012`), and the line in `product-decisions.md` where you settled it names the rule. From a
failing test you can walk back to why the behaviour exists.

Only a rule about what your code does gets a test; tools, configuration and prose get none. The
plan's tasks name the rules they build, each commit ends with the IDs it built, and the reviewer
checks the change against those rules. At the end of a milestone you get a list of every rule:
covered by a test, untested with the reason, or missing.

A rule may carry a tag: `[LATER]` is planned but not built yet, `[VERIFY]` waits for a fact or for
your answer, `[MANUAL]` is one Claude cannot test, so you test it by hand when the milestone ends.

To change what the code does, change the spec first, then the test, then the code.

### Workflow

1. **Brief.** Claude tells you in plain words what the task does, which files it touches, and
   anything the code does that the plan left out. It waits for your go.
2. **Red, Green, then refactor.** It always works using TDD The least code that passes, then a clean-up of what it just wrote.
3. **Report.** The failing assertion from the red run, the test and lint counts, the files
   changed, and anything planned that it did not do.
4. **Commit.** Once, after your yes.

The plan file records each task's status, so a new session picks up where the last one stopped.

A detail no spec rule states is never decided for you. In the plan it appears as a
`Planner choice:` that you accept or cut; during a task Claude stops and asks.

**You merge.** casefile never merges a branch into your default branch and never pushes without
asking.

### Review: a second judgement

The reviewer did not write the change and cannot fix it. It reads the task or issue, the spec rules
and your decisions, runs the tests, and breaks the product code to see whether the tests notice,
restoring every file afterwards. It cannot edit tests, specs, plans, issues or settings, and cannot
switch branches or commit. A change that contradicts a decision or brings back dropped work is a
major finding.

### Decisions: why, and on what evidence

Each decision is one file in `docs/decisions/`: the question that forced it, the real alternatives,
the choice, and what was given up. A decision that is replaced is marked superseded and kept, so
the next reader sees what was already tried.

Claude records a decision when you make one: you pick between options, drop work or reverse
something, even when no file changes. You do not have to ask.

For code that talks to a system you do not control, the same skill makes Claude grade what it
knows before building on it:

| Grade | Source | Trust |
| --- | --- | --- |
| 1 | A live response from the real system | Authoritative |
| 2 | A machine-readable spec fetched from it (OpenAPI, XSD) | Strong |
| 3 | Prose documentation | A hypothesis |
| 4 | "We did not get an error" | Nearly worthless |

## What it keeps in your project

Each folder is proposed the first time it is needed and created only after your yes.

```
docs/
  decisions/                 why: one file per decision, with an index
  specs/                     what: the rules, one file per area
  plans/                     how far: one plan per milestone, with each task's status
  issues/                    bugs, one file each
  product/
    blueprint.html           the build order: the milestones and the rules each one builds
    product-decisions.md     what you settled about the product, one line each
    open-questions.md        what still needs an answer, and what it blocks
    design-system/, design/  copies of your claude.ai designs, when you have them
.claude/
  casefile.json              settings
```

## Settings

`.claude/casefile.json` holds the project's settings. Every key is optional and casefile never
writes the file unasked: `review` and `implement` propose it the first time they run, with the
commands they found in your project.

```json
{
  "default_branch": "main",
  "apps": {
    "web": { "path": "web", "test": "npm test", "lint": "npm run lint", "install": "npm ci",
             "image": "docker compose build web" }
  },
  "protected_paths": ["docs/product/"],
  "design": { "tokens": "docs/product/design-system/tokens.json", "ui_paths": ["web/"],
              "components_dir": "web/components/ui/", "classes": "tailwind" }
}
```

| Key | What it does |
| --- | --- |
| `default_branch` | The branch work starts from and you merge back to. Default `main`. |
| `apps` | One entry per app. `path` is its folder (default: the app's name; `"."` is the whole repository). `test` and the optional `lint` run before every commit that touches the app. `install` installs its locked dependencies. `image` rebuilds its container before a task that touched it is committed. With no apps, commits run no tests. |
| `protected_paths` | Folders the reviewer may not edit, besides tests, specs, plans, issues and `.claude/`. |
| `allow_skip_markers_in` | Folders where a skipped test may be committed. |
| `specs_dir`, `plans_dir`, `build_order` | Where the specs, the plans and the build order are. Defaults: `docs/specs`, `docs/plans`, `docs/product/blueprint.html`. |
| `design` | Turns on the design check for the folders in `ui_paths`: UI code there may use only the colours, spacing, radii, shadows, type styles and components in the `tokens` file. `"classes": "tailwind"` checks Tailwind classes too. Off until both the tokens file and `ui_paths` exist. |
| `repo`, `siblings` | For a frontend and a backend in separate repositories, see below. |

The skipped-test check knows Node and Python test files.

**Frontend and backend in separate repositories.** Give each one `"repo"` (its own name) and
`"siblings"` (the others' names and relative paths, `{"backend": "../backend"}`), and list those
paths in `permissions.additionalDirectories` in `.claude/settings.json`. Both repositories then
hold the same specs and the same plan. Each task names the repository that builds it, and a session
builds only the tasks of the repository it runs in.

**Coming from devflow.** casefile was named devflow before 0.25.0. Rename `.claude/devflow.json` to
`.claude/casefile.json`; while only the old file exists, commits and file edits are refused.

## License

MIT
