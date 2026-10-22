# Evidence skill

The `evidence-based-decisions` skill (`skills/evidence-based-decisions/`) and the `session_start` hook
that points at it. Rules here cover when it triggers and how it brings devflow's documents to their
current format (see D-052); the rest is in `history/`.

### EVID-001 · A request to create, reconcile or update the docs triggers it
Given a project with code
When the developer asks to "create the docs", "reconcile the docs" or "update the docs to devflow's
format"
Then `evidence-based-decisions` triggers.

### EVID-002 · A request for specs does not trigger it
Given a project with code and specs
When the developer asks to "write the specs for a new feature: …"
Then `write-specs` triggers and `evidence-based-decisions` does not.

### EVID-003 · An empty project is handed to write-specs
Given a directory with no code and no documents
When the skill runs
Then it says that `write-specs` starts a new project's specs, and it creates nothing.

### EVID-004 · session_start names documents in an older devflow format
Given a project with a `docs/mental-model.md`, or a `docs/product/product-decisions.md` without its
legend line or with a line that has no ✅ or ❌
When the session starts
Then the injected text names each such file and what is out of date; with none, it injects only the
pointer to the skill. See D-052.

### EVID-005 · The skill rewrites them in the current format      [MANUAL]
Given documents `session_start` named as out of date
When the skill runs
Then it rewrites each in the current format without asking, keeping what is still true, in one commit;
a product decision whose decider the record cannot show is asked, never marked ✅: its line moves to
`open-questions.md` as "Who decided …?" and returns to `product-decisions.md` with ✅ or ❌ once
answered. Critical: the developer approves it on a real repository. See D-052, D-050.

### EVID-006 · Trigger evals can opt out of session-start context
Given an eval case that explicitly sets `EVAL_DEVFLOW_SKIP_SESSION_START=1`
When the session-start hook runs
Then it emits no context, so the case tests the user's request rather than a forced skill call.
An absent flag or any value other than `1` keeps the ordinary session-start behavior; guard hooks
are unaffected. See D-055.
