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
| [D-002](0002-the-repository-root-is-the-plugin.md) | The repository root is the plugin | Accepted |
| [D-003](0003-a-sessionstart-hook-injects-the-trigger.md) | A SessionStart hook injects the trigger a description cannot match | Accepted |
| [D-004](0004-the-hook-injects-a-pointer-not-the-skill-body.md) | The hook injects a pointer, not the skill body | Accepted |
| [D-005](0005-hook-scripts-are-extensionless-behind-a-polyglot-wrapper.md) | Hook scripts are extensionless, behind a cmd/bash polyglot wrapper | Accepted |
| [D-006](0006-the-decision-log-is-one-decision-per-file.md) | The decision log is one decision per file, from entry one | Accepted |
| [D-007](0007-decided-by-is-resolved-from-blame.md) | `Decided by` is resolved from blame, never from `git config` | Accepted |
| [D-008](0008-each-rule-is-stated-once-in-the-place-it.md) | Each rule is stated once, in the place it applies | Accepted |
| [D-009](0009-the-proposed-doc-set-includes-project-instructions.md) | The proposed doc set includes project instructions | Accepted |
| [D-010](0010-watermark-extraction-uses-posix-sed-and-guards.md) | Watermark extraction uses POSIX `sed` and guards the empty case | Accepted |
| [D-011](0011-the-doc-set-gains-a-purpose-document.md) | The doc set gains a purpose document | Accepted |
| [D-011b](0011b-the-doc-set-gains-a-requirements-document.md) | The doc set gains a requirements document | SUPERSEDED by D-023 |
| [D-012](0012-the-skill-runs-on-sonnet-not-opus.md) | The skill runs on Sonnet, not Opus | Accepted |
| [D-013](0013-scaffolding-runs-before-init.md) | Scaffolding runs before `/init` | SUPERSEDED by D-022 |
| [D-014](0014-a-scaffold-is-planned-on-disk-before-any.md) | A scaffold is planned on disk before any command runs | Accepted |
| [D-015](0015-generator-commands-carry-their-verification-state.md) | Generator commands carry their verification state | Accepted |
| [D-016](0016-the-design-system-is-a-separate-skill.md) | The design system is a separate skill | Accepted |
| [D-017](0017-the-radix-branch-authors-its-primitives-rather-than.md) | The Radix branch authors its primitives rather than shipping them | Accepted |
| [D-018](0018-three-actor-classes-and-a-derived-client-count.md) | Three actor classes, and a derived client count | Accepted |
| [D-019](0019-parallel-dispatch-over-a-round-table.md) | Parallel dispatch over a round table | Accepted |
| [D-020](0020-the-seeding-path-splits-by-evidence-grade.md) | The seeding path splits by evidence grade | Accepted |
| [D-021](0021-the-frontend-actor-drafts-the-design-direction.md) | The frontend actor drafts the design direction | Accepted |
| [D-022](0022-the-cast-replaces-the-scaffolder.md) | The cast replaces the scaffolder | Accepted, supersedes D-013 |
| [D-023](0023-requirements-leaves-the-evidence-skills-doc-set.md) | Requirements leaves the evidence skill's doc set | Accepted, supersedes D-011b |
| [D-024](0024-skill-authoring-follows-a-version-watermarked-vendor-digest.md) | Skill authoring follows a version-watermarked vendor digest, and references never nest | Accepted |
| [D-025](0025-the-casts-prompts-are-fixed-templates-and-actor-models.md) | The cast's prompts are fixed templates, and actor models are set per dispatch | Accepted |

## Conventions

- `NNNN-kebab-slug.md`, four digits, slug from the first eight words of the title. The file opens
  with `# D-NNN — Title`.
- The highest filename is the id pointer. Nothing to bump, nothing to contend over.
- Inserting between two ids takes a letter suffix — `0003b-…` — so no `see D-NNN` is invalidated.
- Superseding is marked on the entry's **`Status`** line, and the superseded file stays under its
  original name.
- Full format, attribution procedure and what earns an entry:
  `skills/evidence-based-decisions/references/decision-log.md`.
