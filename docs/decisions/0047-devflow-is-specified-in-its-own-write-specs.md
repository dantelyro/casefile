# D-047 — devflow is specified in its own write-specs layout and built with implement

**Status:** Accepted (2026-10-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-19: "this project it not follow how it own skill define the documents that is what a want", and "yes to all, build it with implement".

**Context:** devflow told every project to keep rules with IDs, a specs README, product decisions, open questions and a build order, and to build milestones through implement, while devflow itself kept one prose design and one hand-run plan per release. Its own convention was never exercised on its own repository. The six existing designs contain example rules (MATCH-010, MATCH-003) that spec_lint would read as devflow's.

**Options:** (a) keep one design doc and a hand-run plan per release; (b) the write-specs layout from M1 on, with earlier designs moved to docs/specs/history/ (outside spec_lint's scan) and existing behaviour specified area by area later; (c) migrate every shipped release into rules before the next release.

**Decision:** (b), the developer's call. docs/specs/ holds README.md and area files with rule IDs; docs/product/ holds blueprint.md (build order), product-decisions.md and open-questions.md; .claude/devflow.json names the Markdown build order. Milestones are planned by devflow:planner and built with implement. Agent and skill behaviour that no unit test can run is tagged [MANUAL]; hook and script rules are [MVP] with tests named after them.

**Trade-offs:** Two sources describe shipped behaviour until each area is specified: history designs and rules, the rules winning. Every release now pays for a plan, agents and reviews, and the tools being changed also build the change. Links into the moved designs were rewritten in 18 files.
