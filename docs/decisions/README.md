# Decision log

Why this repo is the way it is, and what was given up. Git shows *what* changed; these entries
record the reasoning and the trade-offs, so a future reader can tell whether they still hold.

This index carries id, title and status only. Reasoning lives in the entry files — the moment it
appears here as well, there are two places to update and they will disagree.

**D-001 to D-008 are reconstructions**, seeded retroactively on 2026-08-27. Each says so in its
opening blockquote, separating what was read from a commit body or source comment — the author's own
reasoning — from what was inferred. A reconstructed log is worth having, and worth less than a
contemporaneous one. **From D-009 onward the entries are contemporaneous**, recorded in the same
change that implements them; D-009 to D-012 were written on the seeding day like the rest, but
record calls made in that session rather than reconstructed ones, and their `Decided by` lines say
so.

| Id | Title | Status |
| --- | --- | --- |
| [D-001](0001-skill-content-splits-across-two-loading-tiers.md) | Skill content splits across two loading tiers | Accepted |
| [D-002](0002-the-repository-root-is-the-plugin.md) | The repository root is the plugin | SUPERSEDED by D-054 |
| [D-003](0003-a-sessionstart-hook-injects-the-trigger.md) | A SessionStart hook injects the trigger a description cannot match | Accepted |
| [D-004](0004-the-hook-injects-a-pointer-not-the-skill-body.md) | The hook injects a pointer, not the skill body | Accepted |
| [D-005](0005-hook-scripts-are-extensionless-behind-a-polyglot-wrapper.md) | Hook scripts are extensionless, behind a cmd/bash polyglot wrapper | SUPERSEDED by D-028 |
| [D-006](0006-the-decision-log-is-one-decision-per-file.md) | The decision log is one decision per file, from entry one | Accepted |
| [D-007](0007-decided-by-is-resolved-from-blame.md) | `Decided by` is resolved from blame, never from `git config` | Accepted |
| [D-008](0008-each-rule-is-stated-once-in-the-place-it.md) | Each rule is stated once, in the place it applies | Accepted |
| [D-009](0009-the-proposed-doc-set-includes-project-instructions.md) | The proposed doc set includes project instructions | Accepted |
| [D-010](0010-watermark-extraction-uses-posix-sed-and-guards.md) | Watermark extraction uses POSIX `sed` and guards the empty case | Accepted |
| [D-011](0011-the-doc-set-gains-a-purpose-document.md) | The doc set gains a purpose document | Accepted |
| [D-011b](0011b-the-doc-set-gains-a-requirements-document.md) | The doc set gains a requirements document | SUPERSEDED by D-023 |
| [D-012](0012-the-skill-runs-on-sonnet-not-opus.md) | The skill runs on Sonnet, not Opus | Accepted |
| [D-013](0013-scaffolding-runs-before-init.md) | Scaffolding runs before `/init` | SUPERSEDED by D-022 |
| [D-014](0014-a-scaffold-is-planned-on-disk-before-any.md) | A scaffold is planned on disk before any command runs | SUPERSEDED by D-026 |
| [D-015](0015-generator-commands-carry-their-verification-state.md) | Generator commands carry their verification state | SUPERSEDED by D-026 |
| [D-016](0016-the-design-system-is-a-separate-skill.md) | The design system is a separate skill | Accepted |
| [D-017](0017-the-radix-branch-authors-its-primitives-rather-than.md) | The Radix branch authors its primitives rather than shipping them | SUPERSEDED by D-026 |
| [D-018](0018-three-actor-classes-and-a-derived-client-count.md) | Three actor classes, and a derived client count | SUPERSEDED by D-026 |
| [D-019](0019-parallel-dispatch-over-a-round-table.md) | Parallel dispatch over a round table | SUPERSEDED by D-026 |
| [D-020](0020-the-seeding-path-splits-by-evidence-grade.md) | The seeding path splits by evidence grade | Accepted |
| [D-021](0021-the-frontend-actor-drafts-the-design-direction.md) | The frontend actor drafts the design direction | SUPERSEDED by D-026 |
| [D-022](0022-the-cast-replaces-the-scaffolder.md) | The cast replaces the scaffolder | SUPERSEDED by D-026, supersedes D-013 |
| [D-023](0023-requirements-leaves-the-evidence-skills-doc-set.md) | Requirements leaves the evidence skill's doc set | Accepted, supersedes D-011b |
| [D-024](0024-skill-authoring-follows-a-version-watermarked-vendor-digest.md) | Skill authoring follows a version-watermarked vendor digest, and references never nest | Accepted |
| [D-025](0025-the-casts-prompts-are-fixed-templates-and-actor-models.md) | The cast's prompts are fixed templates, and actor models are set per dispatch | SUPERSEDED by D-026 |
| [D-026](0026-mvp-and-project-specs-are-removed.md) | `mvp` and `project-specs` are removed | Accepted, supersedes D-014, D-015, D-017, D-018, D-019, D-021, D-022, D-025 |
| [D-027](0027-hooks-are-standard-library-python-310-tested-with-unittest.md) | Hooks are standard-library Python ≥ 3.10, tested with unittest | Accepted |
| [D-028](0028-enforcement-hooks-fail-closed-and-are-plugin-wide.md) | Enforcement hooks fail closed and are plugin-wide | Accepted, supersedes D-005 |
| [D-029](0029-git-push-asks-the-developer-and-is-denied.md) | `git push` asks the developer and is denied to every agent | Accepted |
| [D-030](0030-workflows-ship-as-plugin-agents-plus-skills-one.md) | Workflows ship as plugin agents plus skills, one spec and one release each | Accepted |
| [D-031](0031-merging-is-the-main-sessions-job-after-the.md) | Merging is the main session's job, after the developer's yes for each change | Accepted |
| [D-032](0032-instructions-used-by-more-than-one-skill-live.md) | Instructions used by more than one skill live in `shared/` | Accepted |
| [D-033](0033-bugs-are-issues-fixed-on-their-own-branch.md) | Bugs are issues in `docs/issues/`, fixed on their own branch; a blocking bug blocks by reference | Accepted |
| [D-034](0034-rules-with-ids-are-the-unit-of-specification.md) | Rules with IDs are the unit of specification, testing and review | Accepted |
| [D-035](0035-the-orchestrator-never-writes-product-code-tests-or.md) | The orchestrator never writes product code, tests or specs; the plan file is the progress record | Accepted |
| [D-036](0036-a-task-that-conflicts-at-merge-is-redone.md) | A task that conflicts at merge is redone from the default branch, never resolved in place | Accepted |
| [D-037](0037-product-answers-and-logged-decisions-are-kept-apart.md) | Product answers and logged decisions are kept apart, and nothing is accepted by silence | Accepted |
| [D-038](0038-the-decision-logs-numbering-entries-and-index-are.md) | The decision log's numbering, entries and index are scripts | Accepted |
| [D-039](0039-designs-live-in-the-project-as-copies-of.md) | Designs live in the project as copies of their artifacts | Accepted |
| [D-040](0040-devflow-proposes-worktree-baseref-head-with-devflow-json.md) | Devflow proposes worktree.baseRef head with devflow.json | Accepted |
| [D-041](0041-sibling-repositories-hold-the-same-specs-and-plan.md) | Sibling repositories hold the same specs and plan, and each builds its own tasks | Accepted |
| [D-042](0042-devflows-setup-makes-the-projects-tools-ignore-agent.md) | Devflow's setup makes the project's tools ignore agent worktrees, and runs lint when the project has it | Accepted |
| [D-043](0043-devflow-agents-run-one-command-per-call-with.md) | Devflow agents run one command per call, with a timeout, and never wait in a loop | Accepted |
| [D-044](0044-what-no-spec-rule-states-is-a-planner.md) | What no spec rule states is a planner choice the developer accepts or cuts | Accepted |
| [D-045](0045-the-reviewer-runs-the-breaks-in-its-own.md) | The reviewer runs the breaks in its own worktree; the implementer no longer proves its own tests | Accepted |
| [D-046](0046-tests-for-existing-code-are-specified-by-write.md) | Tests for existing code are specified by write-specs and built by implement; there is no separate test-writing skill | Accepted |
| [D-047](0047-devflow-is-specified-in-its-own-write-specs.md) | devflow is specified in its own write-specs layout and built with implement | Accepted |
| [D-048](0048-development-uses-uv-pytest-and-ruff-only-shipped.md) | Development uses uv, pytest and ruff; only shipped code stays standard library | Accepted |
| [D-049](0049-devflow-drops-the-mvp-tag-and-adds-no.md) | devflow drops the MVP tag and adds no test tag; what gets a test follows from the project's own code | Accepted |
| [D-050](0050-the-architecture-document-is-overview-md-built-from.md) | The architecture document is overview.md, built from fixed sections | Accepted |
| [D-051](0051-product-decisions-say-who-settled-them-with-or.md) | Product decisions say who settled them, with ✅ or ❌ | Accepted |
| [D-052](0052-devflow-keeps-its-documents-in-its-current-format.md) | devflow keeps its documents in its current format, with no docs skill | Accepted |
| [D-053](0053-a-skills-behaviour-is-tested-by-an-eval.md) | A skill's behaviour is tested by an eval, and MANUAL marks what the developer approves | Accepted |
| [D-054](0054-the-shipped-plugin-lives-in-plugins-devflow-development.md) | The shipped plugin lives in plugins/devflow; development stays at the root | Accepted |

## Conventions

- `NNNN-kebab-slug.md`, four digits, slug from the first eight words of the title. The file opens
  with `# D-NNN — Title`.
- The highest filename is the id pointer. Nothing to bump, nothing to contend over.
- Inserting between two ids takes a letter suffix — `0003b-…` — so no `see D-NNN` is invalidated.
- Superseding is marked on the entry's **`Status`** line, and the superseded file stays under its
  original name.
- Full format, attribution procedure and what earns an entry:
  `skills/evidence-based-decisions/references/decision-log.md`.
