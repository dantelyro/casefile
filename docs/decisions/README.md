# Decision log

Why this repo is the way it is, and what was given up. Git shows *what* changed; these entries
record the reasoning and the trade-offs, so a future reader can tell whether they still hold.

This index carries id, title and status only. Reasoning lives in the entry files — the moment it
appears here as well, there are two places to update and they will disagree.

**This log was seeded retroactively on 2026-08-27.** Every entry is a reconstruction and says so
in its opening blockquote, separating what was read from a commit body or source comment — the
author's own reasoning — from what was inferred. A reconstructed log is worth having, and worth
less than a contemporaneous one.

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

## Conventions

- `NNNN-kebab-slug.md`, four digits, slug from the first eight words of the title. The file opens
  with `# D-NNN — Title`.
- The highest filename is the id pointer. Nothing to bump, nothing to contend over.
- Inserting between two ids takes a letter suffix — `0003b-…` — so no `see D-NNN` is invalidated.
- Superseding is marked on the entry's **`Status`** line, and the superseded file stays under its
  original name.
- Full format, attribution procedure and what earns an entry:
  `skills/evidence-based-decisions/references/decision-log.md`.
