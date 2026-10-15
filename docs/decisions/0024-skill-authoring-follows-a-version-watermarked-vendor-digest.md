# D-024 — Skill authoring follows a version-watermarked vendor digest, and references never nest

**Status:** Accepted (2026-10-08).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session.

**Context:** In one session, three things this repo's skills depend on turned out to have changed
or to differ from recall: Claude Code 2.1.277 began reading `AGENTS.md` as a fallback, the skill
description cap in the Claude Code docs (1,536 characters with `when_to_use`) differs from the one
in the platform best-practices guide (1,024), and the best-practices guide documents that a file
reached through another reference may be previewed with `head -100` rather than read. That last
one is Grade 2 — vendor documentation, worded as "may" — not an observed behaviour. devflow had
been written against none of these sources, and has ten references over 100 lines without a
contents section and three reference-to-reference links.

**Options:** (a) re-check the vendor docs ad hoc when something looks off; (b) keep a digest of the
vendor's skill rules in the repo, watermarked with the Claude Code version it was verified against,
loaded every session and re-checked when the running version moves; (c) the same digest, re-checked
by a hook script rather than an instruction.

**Decision:** (b). The digest is `docs/skill-authoring.md`, imported from `CLAUDE.md`, and the
version comparison is a session-start instruction there. (a) is what produced the drift. (c) was
refused for now: the SessionStart hook ships to every user of the plugin, while this check concerns
only the people editing the skills, and a hook cannot fetch and read a changelog — it could only
announce that the version moved.

On top of the vendor's "keep references one level deep", the user set a stricter rule for devflow:
**references never nest at all**, including links from one skill's references into another skill's.
The vendor's version permits a reference to point at a sibling as long as `SKILL.md` also links it;
the strict form removes the judgement call.

The digest also surfaced a conflict with this repo's own register: Anthropic says to "state what to
do rather than narrating how or why", while devflow's skills carry the reason for each rule. The
user kept reasons, narrowed: a reason stays only when it carries project knowledge the model cannot
infer. Dropping reasons wholesale was refused because the reasons here are mostly local — a rule
without one is the kind that gets optimised away — and the vendor's own examples target explanations
of general knowledge, not of local constraints.

**Trade-offs:** The digest is loaded into every session in this repo, roughly 150 lines of standing
cost. The check relies on the model following an instruction at session start, which is the weaker
mechanism the digest itself warns about. And the digest is a summary: a fact can be wrong in it while
right at the source, which is why every line cites its page and the check re-reads the pages, not
the file. At the time of this entry the repo still violates the no-nesting rule in about
eighteen places — three in `skills/mvp/references/`, one in `living-documents.md`, and the rest
among `project-specs`' references, which name each other by bare filename.

**Changed by:**
- 2026-10-14 · dantelyro — D-026 removed mvp and project-specs; of the ~18 nesting violations counted here, only the one in living-documents.md remains.
