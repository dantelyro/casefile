# D-080 — A C# test names its rule with an xUnit trait, not a prefix in its name

**Status:** **SUPERSEDED by D-081 (2026-11-20).** A test names its rule in a `Rule:` comment above it, in C# as in every other language; the trait was never built.
**Decided by:** dantelyro — Grade 1: decided in the personal-job-tracker session on 2026-11-20, relayed in this change's brief

**Context:** casefile ties a test to its spec rule by the rule ID at the start of the test's name (it('MATCH-010: …'), def test_MATCH_010_…), and rules_coverage.py found only JS/TS and Python test files, so every rule tested in C# was reported missing. The developer's personal-job-tracker project moved to .NET 10 and asked casefile to support it. A C# method name cannot hold a hyphen, so the JS form is impossible and the Python form (Test_ARCH_001_…) fights .NET naming conventions.

**Options:** (a) a name prefix like Python's, ARCH_001_Default_path_…; (b) xUnit's trait, [Trait("Rule", "ARCH-001")], the idiomatic way to attach metadata to an xUnit test and filterable with dotnet test --filter Rule=ARCH-001; (c) a custom attribute such as [Rule("ARCH-001")], which needs a shared helper in every project.

**Decision:** (b), the developer's choice on 2026-11-20 in the personal-job-tracker session, who asked to 'update casefile to do it'. The key may be the literal "Rule" or a constant whose last segment is Rule (Traits.Rule), since that project keeps magic strings out of its tests. rules_coverage.py treats *Tests.cs and *Test.cs as test files and also accepts NUnit's [Category("ARCH-001")] and MSTest's [TestCategory("ARCH-001")], the same idea in the other two frameworks; the value must match rule_id_pattern, so an ordinary category such as "Integration" never counts. The guidance (build-task, specs-layout, planning, reviewer, README) names only the xUnit form.

**Trade-offs:** C# is the one language where the rule is not in the test's name, so a failing test's output shows the rule only when the runner prints traits. The file patterns are fixed in the script, not configurable: a C# test file named otherwise (FooSpecs.cs) is not scanned. The pre-commit hook's skip-marker check and the reviewer's test-file guard still know nothing about C# ([Fact(Skip = …)] is not caught); test files under a tests/ folder are guarded by path.
**Changed by:**
- 2026-11-20 · dantelyro — superseded by D-081 before it was built: the rule ID belongs in a comment, the same in every language, not in a trait.
