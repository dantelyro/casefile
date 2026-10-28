# Claims

How the evidence skill finds false and outdated claims in a project's documents: a script at every
reconciliation, a full read on request, and a version on every claim about an outside system (see
D-062).

### CLAIM-001 · A cited decision that does not exist is flagged
Given a scanned document that cites a decision ID such as `D-071`
When `claims_check.py` runs and the decision log holds no entry with that ID
Then it prints `<file>:<line> D-071 does not exist`

### CLAIM-002 · A cited decision that is superseded is flagged
Given a scanned document that cites a decision ID
When that entry's `Status` line says it is superseded
Then `claims_check.py` prints `<file>:<line> D-NNN is superseded by D-MMM`

### CLAIM-003 · A decision ID matches only as a whole word
Given a line holding `GUARD-005` or `AD-005`
When `claims_check.py` looks for decision IDs
Then it finds none: only `D-NNN`, with an optional letter suffix (`D-011b`), standing as a whole
word is a decision ID

### CLAIM-004 · A path or link that does not exist is flagged
Given a scanned document holding a backticked path (no spaces, at least one `/`) or a relative
Markdown link
When neither the repository root nor the document's own folder holds it, or it is a glob that
matches no file
Then `claims_check.py` prints `<file>:<line> <path> does not exist`; URLs, `#` anchors and paths
holding a placeholder (`<…>`, `${…}`, `$VAR`) are not checked

### CLAIM-005 · A line marked claim-ok is not checked
Given a scanned line holding `<!-- claim-ok -->`
When `claims_check.py` runs
Then nothing on that line is flagged, so a line can name a file because it must not exist

### CLAIM-006 · A claim verified against an older Claude Code is listed
Given a scanned line holding `verified against Claude Code <version>`
When `claims_check.py` runs with `--claude-version` newer than that version
Then it prints `<file>:<line> verified against Claude Code <version>, running <newer>`; without
`--claude-version` it compares nothing

### CLAIM-007 · The result is never silently empty
Given `claims_check.py` has run
When it found something, found nothing, or found no document to scan
Then it exits 1 having printed one line per finding; exits 0 printing how many documents and lines
it checked; or exits 1 saying no document was found

### CLAIM-008 · Which documents are scanned
Given a project
When `claims_check.py` chooses what to scan
Then by default it scans whichever of `CLAUDE.md`, `AGENTS.md`, `docs/architecture/overview.md` and
`README.md` exist; a `claim_docs` list in `.claude/casefile.json` replaces that default; files under
the decision log and `docs/specs/history/` are never scanned, because they cite superseded entries
on purpose

### CLAIM-009 · Reconciliation ends with the claim check      [MANUAL]
Given the evidence skill reconciling a project
When it has replayed the log and run the `git diff --stat` cross-check
Then it runs `claims_check.py` with the running Claude Code version, and fixes each finding or
reports it to the developer

### CLAIM-010 · A full audit gives every claim a verdict      [MANUAL]
Given the developer asks to audit a project's documents for false or outdated claims
When the evidence skill audits them
Then every factual claim gets a row: the claim, what it was checked against, and a verdict — true,
false, or an unverified claim about an outside system; false claims are fixed as step 6 of the
skill says

### CLAIM-011 · A claim about an outside system carries its version      [MANUAL]
Given the evidence skill writing or correcting a claim about a system the project does not control
When it writes the claim
Then the claim carries `verified against <system> <version>` (for Claude Code,
`verified against Claude Code <version>`) and the date

### CLAIM-012 · The description triggers on auditing documents' claims      [MANUAL]
Given a fresh session in a project with documents
When the developer asks to find false or outdated claims in them
Then the evidence skill triggers
