# D-062 — Claims are checked by a script at every reconciliation and by a full read on request

**Status:** Accepted (2026-10-28).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-28, in the developer's words quoted under Context.

**Context:** Reconciliation reads only what landed since the watermark, so a claim already false before it is never looked at again: CLAUDE.md said the greenfield workflows 'land one release at a time, write-specs among them' from 9f4bb76 (2026-10-16), the reconciliation through eb7f238 (2026-10-21) missed it, and only a full read on 2026-10-27 found it. Claims about outside systems go stale with no commit at all. A prototype of the mechanical checks over CLAUDE.md, README.md and the blueprint found no real error and three false positives: a path named because it must not exist, a folder that exists only while an agent runs, and GUARD-005 read as D-005. The developer asked how to make the skill look for false or outdated claims, then chose this design through write-specs: 'go with write-specs', 'so a on both then', 'ok build m6'.

**Options:** (a) a full read only, when asked; (b) a script only, every reconciliation; (c) both, plus a 'verified against' version on every claim about an outside system, which the script compares for Claude Code.

**Decision:** (c), as CLAIM-001..012 in milestone M6. The script checks cited decisions, paths and links, and Claude Code versions; a line holding <!-- claim-ok --> is skipped; it scans the project instructions, the architecture overview and README.md unless claim_docs says otherwise, and never the decision log or specs history.

**Trade-offs:** The script catches only what is mechanical: a sentence that has become false, the kind actually missed here, still needs the full read, which costs a reading of every document and so runs only on request. Each skipped line carries a marker in the document. Only Claude Code versions are compared automatically; other outside systems are checked when the full audit runs.

**Changed by:**
- 2026-10-28 · dantelyro — CLAIM-013 added (the overview's folder tree), and CLAIM-004 checks a lone folder name against every tracked folder; the overview was rejected as the reference because it is one of the documents checked.
