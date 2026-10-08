# Frontend — Vue / Quasar

**The legacy stack, deliberately frozen.** Its value is that it is the same in every project it
appears in. Adding to it costs more than it returns.

| Concern | Choice |
|---|---|
| Framework | Quasar v2 |
| Build | Vite |
| Language | TypeScript, `<script setup>` |
| Client state | Pinia |
| HTTP | axios |
| Forms | Quasar's `QForm` rules; VeeValidate only if a form genuinely outgrows them |
| Styling | SCSS — `quasar.variables.scss` is the theme seam |
| Tests | Vitest `globals: true`, jsdom, Testing Library |

## What does not go here

**No TanStack Query**, though `@tanstack/vue-query` exists. Server data goes through axios, into
Pinia or component state.

**No new state library, no new router, no new component set.** Quasar brings vue-router and its
own components; that is the arrangement.

If a project genuinely needs the newer patterns, it is a React project. That is what question 7
is for.

## Not found and errors

Quasar's template already ships an `ErrorNotFound` page and the catch-all route that reaches it —
keep both rather than deleting them. Add the app-level handler (`app.config.errorHandler`) so an
uncaught error renders a page showing the correlation id from the failed response, rather than a
blank screen.

## Everything else is shared

The invariants apply here unchanged: TypeScript, ESLint, Prettier, Husky, Vitest with globals and
a setup file loading `.env.test`, `src/test` for configuration only, Sentry, semantic-release, the
GitLab pipeline.

Origin topology follows the shape, as on React: **monolith** proxies `/api` to the backend in
development and is served by the backend in production; **separated** points `VITE_API_URL`
straight at the backend, in development too, so a broken CORS configuration surfaces locally.

## Generator

`npm init quasar@latest` is a wizard and the most likely command in the whole skill to hang a
session. Drive it only with its recorded answer sequence.
