# Planning a milestone

How `implement` writes a milestone's plan in the main session (ORCH-015). Read `.claude/casefile.json`
first for where things are (defaults in brackets): the build order (`build_order`
[`docs/product/blueprint.html`], section "Build order"), the specs (`specs_dir` [`docs/specs`]) and their
README, and the plans (`plans_dir` [`docs/plans`]), whose earlier files show the conventions.

## Process

1. Find the milestone's scope in the build order.
2. **Check it against the history**: the decision index and, in full, every decision touching the
   milestone's rules or files; the product decisions and open questions. This is the last point where a
   milestone can be stopped before code is written (D-065).
   - A rule or task that brings back something dropped, reverted or superseded is not planned. It goes
     under Blockers, naming the decision and saying that bringing it back needs a new entry superseding it.
   - One that contradicts an accepted decision or a product decision goes under Blockers naming both.
3. Collect every rule in scope except `[LATER]`; `[VERIFY]` rules, and anything the specs leave
   undecided that a task would have to decide, go under Blockers (RULE-002). Skip rules that already
   have a passing test named after them.
4. **What gets a test** (RULE-004): a test named after a rule only when the rule describes something the
   project's own code does, covering its normal, edge and failure cases. Any other rule gets no test,
   `[MANUAL]` ones included, and its plan line states why (RULE-005). Never a test for tools, packages,
   config or prose.
5. Split the work into small tasks: one behaviour, usually 1–3 rule IDs, at most ~5 files, each
   depending only on earlier ones.
6. For each task, search the code for functions, components, types, fixtures and tests it can use, and
   name each on its `Reuse:` line by file and symbol; none found → say what you searched for. Code
   written twice is a review finding (REV-009).
7. A detail no rule states that a test needs — a value, an extra condition, a data shape — is a
   `Planner choice:` in the task's Notes, for the developer to accept or cut (D-044). Never an invented
   requirement; a test's input never comes from another user's data or depends on test order.
8. With `siblings` in the config, plan the whole milestone in every repository and name each task's
   repository on its `Repo:` line.

## Format

```
# Plan: <milestone> <name>
Planned: <YYYY-MM-DD>
History checked: <decision IDs read in full, and each history file read or absent>

Scope (build order): <what the build order says this milestone covers>
What exists already: <what the code already has that the tasks build on>

## Tasks
### T1 · <short title>
- Status: todo
- Rules: <RULE-ID>, <RULE-ID>
- Repo: <repository whose code the task changes; only with `siblings` in the config>
- App: <app folder from that repository's config, or repo>
- Test first: <test file> — <test names, each starting with its rule ID>, or `none (no test: <reason>)`
- Then implement: <files to create or change>
- Reuse: <file and symbol, each> | none found (searched: <terms>)
- Done when: <one observable check, e.g. "uv run pytest -q passes in worker/">
- Depends on: <task IDs, or none>
- Notes: <what the build must not miss; anything no spec rule states starts with `Planner choice:`>

## Rules covered
- <RULE-ID>, <RULE-ID> → <task IDs>
- ORCH-016 → T4 (no test: skill prose, checked by hand)

## Blockers
<[VERIFY] rules, undecided questions with the options, tools to install; or "none">
```

A rule line with no test named after the rule needs `(no test: <reason>)`; `rules_coverage.py` reports a
rule with neither as missing.
