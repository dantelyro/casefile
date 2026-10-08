# Release and CI

## semantic-release

Fully automatic, versioned from conventional commit prefixes.

```bash
npm i -D semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/gitlab
```

Plugins, in order:

1. `@semantic-release/commit-analyzer`
2. `@semantic-release/release-notes-generator`
3. `@semantic-release/changelog`
4. `@semantic-release/npm` with `npmPublish: false` — these are applications; set `"private": true`
5. `@semantic-release/gitlab`
6. `@semantic-release/git` — commits the bumped manifest and changelog back to `main`

**`@semantic-release/git` is not optional here.** Without it, semantic-release deliberately does
not commit the version back, so `package.json` sits at its seed value forever while tags move on.
The manifest stops describing what shipped, and it is discovered months later.

## `.gitlab-ci.yml`

Two stages:

- **test** — install, lint, typecheck, and the suite against a `postgres` service
- **release** — semantic-release, on `main` only

**No deploy stage.** Deployment belongs to whoever owns it; scaffolding a stage they will replace
is worse than leaving the seam clean.

## The token that will break the first run

`CI_JOB_TOKEN` **cannot push to a protected branch**, and `main` is protected. `@semantic-release/git`
pushes to `main`. So the release job needs a **Project Access Token** with `api` scope and the
Maintainer role, exposed as a CI/CD variable, and allowed to push to `main`.

Without it the job fails at the last step, *after* tagging — the confusing failure mode, because
everything up to the push looks like it worked.

**The skill cannot create that token.** It scaffolds the config and the pipeline, then tells the
user exactly what to create and where. Say it at the end of phase 4, not in a comment nobody
reads.

The `@semantic-release/git` default commit message already carries `[skip ci]`, so the bot commit
does not retrigger the pipeline.
