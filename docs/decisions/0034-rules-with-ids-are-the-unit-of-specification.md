# D-034 — Rules with IDs are the unit of specification, testing and review

**Status:** Accepted (2026-10-14).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: approved with the 0.15.0 spec
(`docs/specs/2026-10-14-implement-design.md`) on 2026-10-14.
**Implemented by:** `9d894b4` — 2026-10-15 (`plan_status.py`), `e8d5a96` (`rules_coverage.py`),
`2a03d6c` (`devflow:planner`), `2d64684` — 2026-10-16 (`implement`).

**Context:** The pilot project's specs state each behaviour as a heading with a stable ID and a tag —
`### MATCH-010 · Formula     [MVP]` — and its M0/M1 milestones were planned, tested and reviewed
against those IDs. `implement` generalises that workflow to any project, so it has to say what it
needs from the specs it starts from.

**Options:** (a) free-form specs, with the planner extracting behaviours each time; (b) specs where
every behaviour is a heading with an ID and a tag, and every test is named after the rule it proves;
(c) a separate requirements file mapping IDs to text.

**Decision:** (b). The rule ID is the thread through the whole flow: the planner plans `[MVP]` rules,
never `[LATER]`, and lists `[VERIFY]` rules under Blockers; every task names its rules and the tests
named after them; the reviewer checks rule by rule; `rules_coverage.py` reports every rule in a plan's
scope with or without a test named after it, `[MANUAL]` rules being checked in review instead. The
heading format is the only hard requirement; where the specs live is `specs_dir` and the ID shape
`rule_id_pattern` in `.claude/devflow.json`. No rules for the request means `implement` stops and the
specs come first.

**Trade-offs:** Projects whose specs are prose need them rewritten as rules first (`write-specs`,
0.16.0, or by hand). A rule that lives only in a table row has no heading, so its tag is unknown:
`rules_coverage.py` reports it as untracked, never as missing. Coverage proves a test is *named*
after a rule, not that it passed — the spec asked for "passed in the last run", but devflow keeps no
record of test runs; passing is shown by the reviewer and at merge (as in D-033).
