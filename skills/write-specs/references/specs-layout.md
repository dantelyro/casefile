# The specs layout

Inverso's layout is the default. Folders are created only after the developer's yes, and only the
ones the input needs.

```
docs/
  product/
    blueprint.html          the project at a glance; its "Build order" section lists the milestones
    product-decisions.md    what the developer settled about the product, one line each
    open-questions.md       what still needs an answer: question, what it blocks, who answers
    design-system/          a copy of a Design System artifact (tokens, brand, components)
    design/                 a copy of each Design artifact, one folder per screen or flow
  decisions/                the evidence skill's decision log
  specs/
    README.md               how the project works with specs (below)
    01-…, 02-…, 03-…        foundations: product, architecture, data model
    10-… to 2x-…            one file per area (auth, matching, jobs, …), plus testing and deploy
```

## A rule

```
### MATCH-003 · Required skills weigh 70%            [MVP]
Given a job with required and nice-to-have skills
When the score is computed
Then required skills contribute 70 of the 100 points
```

The ID is the area's prefix and a three-digit number. Tags — a rule may carry more than one:
`[MVP]` must ship · `[LATER]` planned, not built yet · `[VERIFY]` depends on an outside fact to
confirm before building · `[MANUAL]` cannot be tested automatically; checked in review or a release
checklist. A rule for a screen links its file under `docs/product/design/`; a component rule links
the component under `docs/product/design-system/`. A rule that exists because of a logged decision
cites it (`see D-012`); the reasoning stays in the entry.

## `docs/specs/README.md`

Written once, for a new project:

```
# Specs

How this project is built:

1. **Spec first.** Every feature has a file here. Each rule has an ID (`MATCH-003`).
2. **Test second.** Before any code, a failing test whose name starts with the rule ID
   (`it("MATCH-003: …")`, `def test_MATCH_003_…`).
3. **Code third.** The least code that makes it pass, then refactor.
4. **Trace.** Every `[MVP]` rule has a test named after it (`rules_coverage.py`).
5. **Change.** To change behaviour: spec (a new or changed ID) → test → code. Never the other way round.

This folder is the source of truth: if code and a spec disagree, the spec wins or is changed first.
`docs/product/product-decisions.md` records what was settled about the product;
`docs/decisions/` records choices between real alternatives, why, and who made them;
`docs/product/open-questions.md` records what is still unanswered and what it blocks.

<the rule format and the tags, as above>

| File | What |
|---|---|
| [01-product.md](01-product.md) | Audience, plans, limits |
```

Every spec file has a row in the table, and every row a file (`spec_lint.py` checks).

## `docs/product/product-decisions.md`

One line per answer: the answer, its date, the rules it produced. No reasoning — that lives in the
rule or the decision entry.

```
- Brazil first, PT-BR only at launch (2026-10-01) → PROD-010, [AUTH-001](../specs/10-auth.md)
- Saved jobs never expire (2026-10-16) → JOBS-020, see D-012
```

## `docs/product/open-questions.md`

```
- Do saved jobs count toward the free limit? Blocks JOBS-022. Answers: the developer.
```

When answered, the line moves to `product-decisions.md` with the date.

## The build order

A section headed "Build order" in the blueprint. Each milestone is a slice that runs end to end, in
order, and **names its rules**, so `spec_lint.py` can check they exist:

```
<div class="ms"><span class="n">M10</span><h3>Saved jobs</h3><p>JOBS-020, JOBS-021, JOBS-022.</p></div>
```

A Markdown blueprint uses a `## Build order` heading with one list item per milestone.
