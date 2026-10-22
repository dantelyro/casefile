---
type: llm
focus:
  source: file
  path: docs/architecture/overview.md
---

Pass only if the overview preserves these facts: src/jobs.js contains saveJob, which returns a copy
of the job with saved set to true; there are no runtime dependencies and no database integration yet.
Fail if any of these facts is omitted or contradicted, or if the overview invents other implemented
components, database persistence, servers, frameworks or services absent from the fixture.
