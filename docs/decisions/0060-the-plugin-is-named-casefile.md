# D-060 — The plugin is named casefile

**Status:** Accepted (2026-10-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 1: decided in session, 2026-10-27, in the developer's words quoted under Context.

**Context:** The developer, 2026-10-27: 'i was planning to change it name from devflow to casefile', then, while the evidence skill was being reworked, 'also remenber to change the name to casefile'. devflow is a generic name; a case file is the folder of evidence and decisions behind a case, and a bug, PR or task is the case the skills work on.

**Options:** For projects that already keep .claude/devflow.json: (a) read it as a fallback in every reader; (b) ignore it and use defaults; (c) refuse it in the hooks with a message to rename it.

**Decision:** The plugin, its agents (casefile:reviewer, casefile:implementer, casefile:planner), the hook package (hooks/casefile_hooks), the injected tag and the settings file (.claude/casefile.json) are renamed; the homepage and repository URLs point at github.com/dantelyro/casefile. (c): lib.config raises ConfigError for a leftover .claude/devflow.json, so every guard fails closed until it is renamed. Historical plans, specs, issues and decision entries keep the old name.

**Trade-offs:** Installed copies do not update: users uninstall devflow and install casefile@dantelyro. The skill scripts (plan_status, issues_status, rules_coverage, spec_lint) read only casefile.json and fall back to defaults if it is missing. (a) would put the old name in five readers for good; (b) would quietly loosen every guard an old file configured.
