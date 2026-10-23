# D-056 — M4 is reverted, and specs for existing code and the docs reconciliation skill are dropped

**Status:** Accepted (2026-10-23).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-23, in the developer's words quoted under Context.

**Context:** M4 (decision icons, the docs trigger, evals as tests; D-051..D-055) was built partly with devflow (T1-T3, T14, T5) and finished outside it by Codex in fa22729..ce66337, which shipped as 0.23.0. The developer: 'i used codex to finish but it made a mess i need to undo M4 completly actually i will drop M4 and M5', then 'b' (drop SPEC-001..005 too, superseding D-046) and 'revert first than drop M4, M5 and this skill' (the docs reconciliation skill, DOCS-001..008, which the revert had restored). What M4 found stays true and is recorded in its commits: agents cannot run claude plugin eval in their worktrees; uv's hard-linked .venv makes claude plugin eval refuse a plugin at the repository root; shell tools in evals need a sandbox native Windows lacks; plugin eval fires SessionStart.

**Options:** (a) revert M4 with one new commit and push normally; (b) reset main to before M4 and force-push; (c) fix M4 in place. For the milestones after M3: keep specs for existing code (SPEC-001..005) and docs reconciliation (DOCS-001..008) as later work, or drop both.

**Decision:** (a), then drop both. a34d1ff restores every file to e7cbef5 (0.22.1's content), keeping only 8edaf23's CLAUDE.md correction; this change removes docs/specs/30-write-specs.md (SPEC-001..005) and docs/specs/40-docs-reconciliation.md (DOCS-001..008), their milestones from the build order and their open questions, marks their product decisions dropped, supersedes D-046, and sets the version to 0.23.1 so installed 0.23.0 copies roll back. The build order ends at M3. D-051..D-055 exist only in history; this entry takes D-056 so no ID cited in a commit message is reused.

**Trade-offs:** Adding tests to existing code and bringing old documents into the layout have no devflow path again. M4's working parts (spec_lint's icon check, rules_coverage counting evals) are gone with the rest and would have to be rebuilt. (b) would rewrite history GitHub already has; (c) would keep work the developer judged a mess.
