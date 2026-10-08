# Generators

Every command that creates something, with its **verification state**.

| State | Meaning |
|---|---|
| `VERIFIED <date>` | Run, output inspected |
| `UNVERIFIED` | Written from documentation or memory. Treat as a hypothesis |
| `INTERACTIVE` | Prompts. Either drive the recorded answer sequence, or do not use it |

**No command in this file carries a version number.** `npm i <pkg>` resolves what current means.

---

## Backend

### Nest — `UNVERIFIED`

```bash
npx @nestjs/cli new <name> --package-manager npm --skip-git --strict
```

Without `--package-manager` it prompts. `--strict` turns on TypeScript strict mode at creation,
which is far cheaper than turning it on later.

Nest defaults to **Jest**, not Vitest. Swapping it is written config, and with Nest it is not
only config: `emitDecoratorMetadata` is what Nest's DI reads at runtime, and esbuild — which
Vitest uses to transform by default — does not emit it. The transform has to be swapped for one
that does (`unplugin-swc` is the usual answer). `UNVERIFIED` — confirm before relying on it.

### Fastify — `UNVERIFIED`

```bash
npm create fastify@latest -- --lang=typescript
```

### Express — no generator

`express-generator` emits JavaScript against an old layout. Do not use it.

```bash
npm init -y
npm i express
npm i -D typescript tsx @types/express @types/node
npx tsc --init
```

Everything else about an Express project is written config, and that is correct — Express has no
opinion to inherit.

---

## Database

### Prisma — `UNVERIFIED`

```bash
npm i -D prisma
npm i @prisma/client
npx prisma init --datasource-provider postgresql
```

### Drizzle — no generator

```bash
npm i drizzle-orm pg
npm i -D drizzle-kit @types/pg
```

`drizzle.config.ts` is written by hand, by design. Not a violation of the core principle.

---

## Frontend

### Vite — `UNVERIFIED`

```bash
npm create vite@latest <name> -- --template react-ts
npm create vite@latest <name> -- --template vue-ts
```

The bare `--` matters: without it npm eats the template flag and the CLI prompts.

### Quasar — `INTERACTIVE`

```bash
npm init quasar@latest
```

A wizard with no documented full non-interactive flag set. **Before using it, check whether the
current CLI accepts flags for every prompt.** If it does not, record the exact answer sequence
here and drive it deliberately:

```
project folder    <name>
project type      App with Quasar CLI
Quasar version    Quasar v2
script type       Composition API with <script setup>
language          TypeScript
bundler           Vite
CSS preprocessor  Sass with SCSS syntax
features          Pinia, Axios, ESLint, Prettier
```

This is the single most likely command in the skill to break. It is also the one whose breakage
is most visible — the session simply stops.

### shadcn/ui — `UNVERIFIED`

```bash
npx shadcn@latest init
npx shadcn@latest add button input label card dialog select
```

Requires Tailwind. Only reachable through question 8.

### Radix — no generator

```bash
npm i radix-ui
```

One unified package that re-exports the primitives — not the twenty-five separate
`@radix-ui/react-*` packages older projects list. The primitive components themselves are written;
see `frontend-react.md`.

### Mantine — `UNVERIFIED`

```bash
npm i @mantine/core @mantine/hooks
npm i -D postcss-preset-mantine postcss-simple-vars
```

---

## Cross-cutting

### Husky — `UNVERIFIED`

```bash
npm i -D husky lint-staged @commitlint/cli @commitlint/config-conventional
npx husky init
```

`husky init` writes `.husky/pre-commit` and adds the `prepare` script. The hook bodies are
written config.

### semantic-release — `UNVERIFIED`

```bash
npm i -D semantic-release @semantic-release/changelog @semantic-release/git @semantic-release/gitlab
```

See `release.md` for configuration and the token that the pipeline needs.

### Sentry

Install directly. `npx @sentry/wizard` is `INTERACTIVE` and edits files it does not own.

```bash
npm i @sentry/node          # backend
npm i @sentry/react         # frontend
```

### TanStack — `UNVERIFIED`

```bash
npm i @tanstack/react-query
npm i @tanstack/react-router
npm i -D @tanstack/router-plugin
```

---

## Verifying a command

Run it in a throwaway directory, inspect what it produced, then change the state in this file to
`VERIFIED <date>` in the same commit. Do not mark a command verified because it looked right.
