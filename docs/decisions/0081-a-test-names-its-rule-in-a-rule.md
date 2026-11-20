# D-081 — A test names its rule in a Rule comment, in every language

**Status:** Accepted (2026-11-20).
**Decided by:** dantelyro — Grade 1: stated in this session on 2026-11-20

**Context:** D-034 tied a test to its spec rule by the rule ID at the start of the test's name: it('MATCH-010: …') in JS/TS, def test_MATCH_010_… in Python. D-080, written the same day for the personal-job-tracker project's move to .NET 10, gave C# an xUnit trait instead, because a C# method name cannot hold a hyphen. Reviewing D-080, the developer objected that the rule ID in a test's name or description pollutes it, and that it belongs in a comment.

**Options:** (a) keep the ID in the name for JS/TS and Python and a trait for C# (D-034 + D-080); (b) each framework's own metadata: Playwright tags, pytest markers, xUnit traits, with nothing for Jest or Vitest; (c) one comment on the test, // Rule: MATCH-010 or # Rule: MATCH-010, the same in every language.

**Decision:** (c), the developer's choice on 2026-11-20: 'the best way to match all languages is by a comment'. One form fits every language and needs no setup in the project. The rule is only that the ID sits in a comment: rules_coverage.py counts any line whose only text before `Rule:` is comment marks (`// Rule: MATCH-010`, `# Rule: MATCH-001, MATCH-002`), in any file but Markdown, with no list of languages, test frameworks or test-file names; the developer asked that it not try to recognise each language's tests. Test names no longer count, so there is one form.

**Trade-offs:** A failing test's output no longer shows its rule; the reader opens the test to see it. The script no longer checks that a test follows the comment: a Rule comment above a helper or a commented-out test counts, and catching that is left to the reviewer. Projects whose tests are named the old way report those rules as missing until each test gets its Rule comment. Runners cannot select by rule (dotnet test --filter, pytest -m).
