# Docs reconciliation

A separate skill that brings a project's documents into `write-specs`' layout. It reconciles
documents with the layout; reconciling them with the code at session start stays the
`evidence-based-decisions` skill's.

### DOCS-001 · It inventories the documents against the layout      [LATER]
Given a project with documents
When the skill runs
Then it lists, against `write-specs`' layout, what exists, what is missing, and what exists in another
form (prose designs, rules written as paragraphs).

### DOCS-002 · It proposes every move before making it      [LATER]
Given the inventory
When the skill proposes the migration
Then it shows each file's destination, and moves nothing before the developer's yes.

### DOCS-003 · Files spec_lint would misread leave its scan      [LATER]
Given a document whose text `spec_lint.py` would read as rules (example rules in an old design)
When the migration is proposed
Then that document moves out of the folder `spec_lint.py` scans.

### DOCS-004 · Moves keep history and leave no broken link      [LATER]
Given files to move
When they are moved
Then each moves with `git mv`, every link to it is rewritten in the same commit, and a script checks
that no relative link is left broken.

### DOCS-005 · Touched files keep their bytes      [LATER]
Given a file the skill edits
When it is written
Then its line endings and encoding are unchanged, and only the edited text differs.

### DOCS-006 · Rules come from write-specs, not from this skill      [LATER]
Given an old document that describes behaviour
When the migration is done
Then the skill writes no rule from it, and hands each area to `write-specs` (SPEC-001).

### DOCS-007 · It ends with the checks passing      [LATER]
Given the migration is written
When the skill finishes
Then `spec_lint.py` passes, and so does `decision_index.py --check` when the project keeps a log.

### DOCS-008 · The description triggers on bringing docs into the layout      [LATER]
Given a request to bring a project's documents in line with devflow ("migrate the docs to the specs
layout")
When skills are matched
Then this skill triggers, and it does not at session start; checked by trigger evals.
