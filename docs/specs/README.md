# Specs

How this project is built:

1. **Spec first.** Every feature has a file here. Each rule has an ID (`REV-001`).
2. **Test second.** Before any code, a failing test whose name starts with the rule ID
   (`def test_GUARD_001_…`).
3. **Code third.** The least code that makes it pass, then refactor.
4. **Trace.** Every `[MVP]` rule has a test named after it (`rules_coverage.py`).
5. **Change.** To change behaviour: spec (a new or changed ID) → test → code. Never the other way round.

This folder is the source of truth: if code and a spec disagree, the spec wins or is changed first.
`docs/product/product-decisions.md` records what was settled about the product;
`docs/decisions/` records choices between real alternatives, why, and who made them;
`docs/product/open-questions.md` records what is still unanswered and what it blocks.

## A rule

```
### GUARD-001 · The reviewer edits only inside a linked worktree      [MVP]
Given the reviewer writes a file
When the file is outside a linked worktree
Then the write is denied
```

The ID is the area's prefix and a three-digit number. Tags — a rule may carry more than one:
`[MVP]` must ship · `[LATER]` planned, not built yet · `[VERIFY]` depends on an outside fact to
confirm before building · `[MANUAL]` cannot be tested automatically; checked in review or a release
checklist. A rule that exists because of a logged decision cites it (`see D-012`); the reasoning
stays in the entry.

Most of devflow's behaviour is agent and skill prose, which a unit test cannot run: those rules are
`[MANUAL]` and are checked by the reviewer, the trigger evals and each release's live test. Rules a
hook or a script enforces are `[MVP]`.

## Files

| File | What |
|---|---|
| [10-guards.md](10-guards.md) | What the hooks let each devflow agent do |
| [20-reviewer.md](20-reviewer.md) | `devflow:reviewer` |
| [21-implementer.md](21-implementer.md) | `devflow:implementer` |
| [30-write-specs.md](30-write-specs.md) | The `write-specs` skill |
| [40-docs-reconciliation.md](40-docs-reconciliation.md) | The docs reconciliation skill |

Behaviour shipped before these files (through 0.19.1) is described in `history/`, one design per
release, and is being specified here area by area. Where a rule here and a history design disagree,
the rule wins.
