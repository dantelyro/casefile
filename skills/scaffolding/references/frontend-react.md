# Frontend — React

The greenfield stack. New things are allowed here; `frontend-vue.md` is where they are not.

## Structure

```
src/
  app/        providers, router, layout, pages
  features/   one folder per feature, self-contained
  shared/     the axios instance, hooks, ui, theme, lib
  test/       setup.ts, render helper, MSW server and handlers — configuration only
```

Enforced by `eslint-plugin-boundaries`: `app` may import anything, `features` may import
`shared` and their own internals but **not sibling features**, `shared` may import only
`shared`, and production code may not import test helpers. A structure that is only a convention
is one people drift out of; as a lint rule it is a build failure.

## Stack

| Concern | Choice |
|---|---|
| Build | Vite + TypeScript |
| Server state | TanStack Query |
| Client state | Zustand |
| HTTP | axios — one configured instance in `shared/`, every interceptor on it |
| Validation | zod, the same schemas the backend uses |
| Forms | react-hook-form + `@hookform/resolvers` |
| Routing | asked — question 9 |
| Components | asked — question 8 |
| Styling | SCSS modules, tokens in one theme file |
| Tests | Vitest `globals: true`, jsdom, `css: true`, Testing Library, MSW |

Query and Zustand are not competing: Query owns anything that came from the server, Zustand owns
anything that did not. Putting server data in Zustand is how a project ends up hand-writing cache
invalidation.

## Component branches

**Radix + own primitives.** Radix ships behaviour with no appearance — focus trapping, keyboard
navigation, ARIA, collision-aware positioning — and you write every line of the styling. The
primitive set lives in `shared/ui`, each one a `.tsx` + `.module.scss` + a colocated test,
reading from the theme tokens: button, input, label, textarea, select, card, badge, dialog,
sheet, toast, skeleton, spinner.

Those primitives are **authored**, not generated. That is consistent with the core principle —
the principle governs versions, not who writes a component — but it is the branch with the most
code to produce, and the plan must say so before the user approves it.

**Mantine.** Components, hooks, notifications and a modals manager already built. Theme through
its CSS variables, extend with `.module.scss`. Fastest to a working screen; you are theming
someone else's design rather than authoring your own.

**shadcn/ui + Tailwind.** Its CLI copies component source into the repo, so you own it — but the
styling is utility classes in the markup, which is the whole objection people have to Tailwind.
Only offer it having said that.

## Origin topology follows the shape

**Monolith** — Vite dev proxy `/api` to the backend; in production the backend serves the built
SPA. Same origin at both ends, so no CORS anywhere.

**Separated** — `VITE_API_URL` points straight at the backend, in development too. Deliberately
**not** proxied: a proxy makes development same-origin, so a broken CORS configuration would
surface at deploy instead of on the machine where it can be fixed. Development should have
production's origin topology.

## Errors

The axios instance parses RFC 9457 problem+json responses back into the same error classes the
backend throws, so a component catches a `ConflictError` instead of reading
`err.response.status === 409`.

## Auth wiring — when auth was chosen

- A working login page and a protected-route guard
- The 401 → refresh → retry interceptor on the axios instance: one retry, and a failed refresh
  logs out rather than looping
- Where the refresh token lives follows the answer to question 5

Styled with whatever the chosen component branch gives out of the box. The visual layer — real
tokens, real screens — is a separate skill's job, and the theme file is the seam it writes into.
