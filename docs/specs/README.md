# Specs

How this project is built:

1. **Spec first.** Every feature has a file here. Each rule has an ID (`REV-001`).
2. **Test second.** For a rule that describes what the project's code does, a failing test whose
   name starts with the rule ID comes before any code (`def test_GUARD_001_…`).
3. **Code third.** The least code that makes it pass, then refactor.
4. **Trace.** Every rule that describes what the project's code does has a test named after it; a rule left untested states why on its plan line (`rules_coverage.py`).
5. **Change.** To change behaviour: spec (a new or changed ID) → test → code. Never the other way round.

This folder is the source of truth: if code and a spec disagree, the spec wins or is changed first.
`docs/product/product-decisions.md` records what was settled about the product;
`docs/decisions/` records choices between real alternatives, why, and who made them;
`docs/product/open-questions.md` records what is still unanswered and what it blocks.

## A rule

```
### GUARD-001 · The reviewer edits only inside a linked worktree
Given the reviewer writes a file
When the file is outside a linked worktree
Then the write is denied
```

The ID is the area's prefix and a three-digit number. A rule needs no tag: it is built in its
milestone. Tags, which a rule may combine: `[LATER]` planned, not built yet · `[VERIFY]` waits for
something to be confirmed before it is built: a fact about an outside system, or the developer's
answer to a question the rule depends on · `[MANUAL]` neither a test nor an eval can check it (how a screen
feels, a live system a run cannot reach, the developer's own judgement), or the developer marked it
critical, so it keeps its test or eval as well; the developer approves each when its milestone
finishes. A rule that exists because of a logged decision cites it (`see D-012`); the reasoning
stays in the entry.

Most of devflow's behaviour is agent and skill prose, which a unit test cannot run: a rule about what
a skill or agent does has an eval named after it (`evals/<RULE-ID>-<slug>/`). Rules a hook or a script
carries out have a test.

## Files

| File | What |
|---|---|
| [10-guards.md](10-guards.md) | What the hooks let each devflow agent do |
| [20-reviewer.md](20-reviewer.md) | `devflow:reviewer` |
| [21-implementer.md](21-implementer.md) | `devflow:implementer` |
| [30-write-specs.md](30-write-specs.md) | The `write-specs` skill |
| [31-rules-and-tests.md](31-rules-and-tests.md) | What tags mean and what gets a test |
| [32-evidence-skill.md](32-evidence-skill.md) | The `evidence-based-decisions` skill and `session_start` |
| [50-tooling.md](50-tooling.md) | Shipped code stays standard library |

Behaviour shipped before these files (through 0.19.1) is described in `history/`, one design per
release, and is being specified here area by area. Where a rule here and a history design disagree,
the rule wins.
