# The question set

Closed, ordered, asked in one pass before anything is written. Nothing outside this file is
asked at all — `invariants.md` holds what is already decided, backend and frontend alike.

Order is not cosmetic: later questions are skipped or constrained by earlier answers.

A question `docs/requirements.md` already settles is recorded from that document, not asked. The
set still stays closed: this reads an existing answer, it does not add a new question.

---

## 1. Shape

| Answer | What it means |
|---|---|
| **Monolith** | One repo. Backend serves the built SPA. Same origin in production. |
| **API only** | One repo, no frontend. |
| **Microservice** | One repo **per service**. Never several services in one repo. |
| **Separated** | **Two independent git repos**, one backend, one frontend. |

Changes downstream: CORS, the frontend's origin topology, whether questions 7–9 are asked at
all, and how many repos the plan creates.

## 2. Backend framework

**Nest · Express · Fastify.** Asked for every shape including the monolith — "monolith" says
nothing about the framework.

## 3. Transport — *microservice only*

Ask the real question first: **does this service take work from a broker, or answer HTTP
requests?**

- **HTTP** — the default. Follow the API-only path and skip the rest of this question.
- **From a broker** — RabbitMQ (recommended), Redis, Kafka, NATS, TCP, gRPC.

RabbitMQ leads because durable queues, retries and dead-lettering are what people get burned for
lacking. Redis pub/sub is right only when losing a message while the consumer is down is
genuinely acceptable. Whatever is chosen becomes another service in the compose file.

## 4. ORM

**Prisma or Drizzle** recommended; TypeORM, MikroORM, Kysely, or none.

**Drizzle has no scaffolder** — its config is written, by design. That is not a violation of the
core principle: the principle is about versions, not about who authors `drizzle.config.ts`.

**None** still gets the compose file and both databases, but no migration step in `predev` — say
what replaces it.

## 5. Auth

**No** — skip to question 6.

**Yes** — local, **bcrypt**. Then the follow-up:

> Refresh-token session validation? If yes, where does the refresh token live?

Present both, and not as equivalents:

- **httpOnly cookie** — unreadable by injected script. The safer default.
- **localStorage / sessionStorage** — readable by any XSS on the page, and the refresh token is
  the long-lived one.

Yes also produces, on the frontend: a working login page, a protected-route guard, and the
401 → refresh → retry interceptor.

## 6. RBAC

Explain before asking — the term is not universal:

> Role-Based Access Control: a user holds roles, and permission to do something is granted to
> the role rather than to the person. "Editors may publish" instead of "these fourteen users may
> publish."

| Answer | What gets built |
|---|---|
| **No** | Nothing. Authenticated or not. |
| **Roles enum** | A hardcoded role list, a guard, a decorator. Around twenty lines. |
| **Permissions tables** | `roles`, `permissions`, `role_permissions`, a seed, and a guard that resolves at request time. |

Enum when the roles are known and stable. Tables when someone non-technical must change who can
do what without a deploy.

## 7. Frontend — *skipped for API only*

**None · Vue/Quasar · React.**

Not equivalent postures. Quasar is the legacy stack and stays frozen (`frontend-vue.md`). React
is where new things are allowed (`frontend-react.md`).

## 8. Components — *React only*

| Answer | Consequence |
|---|---|
| **Radix + own primitives** | Unstyled behaviour; all styling yours in SCSS modules. Deepest customization, most code to write. |
| **Mantine** | ~120 styled components plus hooks, notifications and a modals manager. Fastest to a screen; you theme rather than author. |
| **shadcn/ui + Tailwind** | A CLI copies component source into the repo. Utility classes in the markup — say so when offering it, since that is the whole objection people have to it. |

Each branch has a different theme seam, and that seam is where a future design-system skill
writes: `shared/theme/tokens.scss`, Mantine's CSS variables, or `tailwind.config` plus CSS
variables.

## 9. Router — *React only*

| Answer | What it buys | What it costs |
|---|---|---|
| **TanStack Router** | Params and search params validated by zod at the route, so `?page=abc` never reaches a component. `<Link>` checked against the route tree — a wrong path is a compile error. Loaders integrate with TanStack Query, so data is fetched before render instead of after mount. | More ceremony per route, smaller community, fewer answers when stuck. |
| **React Router** | The default everyone knows. Every question already answered somewhere. | `useParams()` returns `string \| undefined` even when the route guarantees the param. Search params are strings you parse by hand. `<Link to={\`/x/${id}\`}>` typos compile fine and 404 in production. |

The honest split: TanStack Router pays off where URLs carry real state — filter-heavy lists,
paginated tables, anything meant to be shareable and correct. For a handful of straightforward
pages it is ceremony for its own sake.

---

## Not asked

- **CORS** — derived from question 1.
- **Database engine** — Postgres.
- **Package manager** — npm.
- **Architecture** — layered on the backend, feature folders plus a shared layer on the
  frontend, unless the project's purpose contradicts it.
- Everything in `invariants.md`.

Adding a question to this file is a decision. Record it.
