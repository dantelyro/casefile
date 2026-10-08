# Invariants

Never asked, always applied. They exist so that two projects scaffolded a year apart are
recognisably the same project. Every one of them is a default someone would otherwise decide
differently each time.

**None of these is a version.** Install by name and let npm resolve — `npm i -D vitest`, never a
pinned string typed from memory.

---

## Everywhere — backend and frontend

| | |
|---|---|
| Language | TypeScript |
| Node | latest LTS, pinned in `engines` |
| Package manager | npm |
| Lint | ESLint |
| Format | Prettier |
| Git hooks | Husky, with lint-staged and commitlint |
| Tests | Vitest, `globals: true` |
| Test env | setup file loading `.env.test` |
| Test layout | tests beside the source; `test/` (or `src/test/`) holds **configuration only** |
| Env files | `.env`, `.env.test`, `.env.example`, all created; `.env*` ignored except `.env.example` |
| Env validation | a zod schema checked at boot — a missing variable fails at startup, not at 3am |
| Errors | Sentry, DSN from env, silent when the variable is unset |
| Release | semantic-release |
| CI | `.gitlab-ci.yml`, test and release stages. **No deploy stage** — that belongs to whoever owns deployment |
| VCS | `.gitignore` present before the first commit |

**commitlint is not decoration.** semantic-release derives the version from commit prefixes, so a
commit that ignores the convention is a release that does not happen.

## Backend only

- `tsconfig.json` plus `tsconfig.build.json` — the build config excludes tests and specs
- **docker-compose with two Postgres services**: development and test, on different ports
- Database tests are fully isolated and **truncate between every test**
- helmet, rate limiting
- CORS **only where the shape requires it** — separated, or an API a browser on another origin calls
- zod for all input validation
- Swagger/OpenAPI generated, **mounted only outside production**
- Structured logging with a request/correlation id on every line
- Health endpoint
- API versioning from day one — `/v1`
- The error class hierarchy and the single global handler
- `predev` brings up the containers and applies migrations before `dev` runs

## Frontend only

- Vite
- The generator's own `tsconfig.app.json` / `tsconfig.node.json` split satisfies the build-config
  rule; do not add a third
- jsdom, `css: true`, setup at `src/test/setup.ts`
- Testing Library plus `jest-dom`
- axios, one configured instance in `shared/`, all interceptors on it
- zod, sharing schemas with the backend
- SCSS modules; tokens in one theme file
- `src/app` · `src/features` · `src/shared` · `src/test`
- `eslint-plugin-boundaries` enforcing that structure — features may not import sibling features,
  production code may not import test helpers. A structure that is only a convention is one people
  drift out of; as a lint rule it is a build failure.
- `predev` only where there is something to start. In the separated shape the frontend repo has
  nothing to bring up, so it has no `predev`.

## Scripts

Backend: `dev`, `predev`, `build`, `start`, `test`, `test:watch`, `lint`, `format`,
`typecheck`, `migrate`, `db:seed`, `docker:up`, `docker:down`.

Frontend: `dev`, `build`, `preview`, `test`, `test:watch`, `lint`, `format`,
`typecheck`.

A script that exists in one project and not the next is the divergence this file prevents.
