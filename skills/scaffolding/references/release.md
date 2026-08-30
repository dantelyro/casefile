# Release and CI

## semantic-release

Fully automatic. The version is derived from conventional commit prefixes — nobody chooses a
number, and nobody forgets to cut a release.

```bash
npm i -D semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/gitlab
```

Plugins, in order:

| Plugin | Job |
|---|---|
| `@semantic-release/commit-analyzer` | Decides patch / minor / major from the commits |
| `@semantic-release/release-notes-generator` | Writes the notes |
| `@semantic-release/changelog` | Maintains `CHANGELOG.md` |
| `@semantic-release/npm` with `npmPublish: false` | Bumps the manifest. These are applications — set `"private": true` |
| `@semantic-release/gitlab` | Creates the GitLab release against the tag |
| `@semantic-release/git` | Commits the bumped manifest and changelog back to `main` |

**`@semantic-release/git` is not optional here.** Without it, semantic-release deliberately does
not commit the version back, so `package.json` sits at its seed value forever while tags move on.
The manifest stops describing what shipped, and it is discovered months later.

**Conventional commits are load-bearing, not stylistic.** A commit that ignores the convention is
a release that does not happen. That is why commitlint is an invariant.

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
