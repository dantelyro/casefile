# Backend

Layered by default — routes, services, repositories — unless the project's purpose contradicts
it. An event-driven notification service is the standing exception: layering it produces a layer
that exists only to be traversed.

Everything here applies to all three frameworks. Where they differ, it is where the framework
puts the seam, not whether the seam exists.

---

## Error classes

The single most valuable thing this scaffold ships, because it is what every project grows badly
if it does not start with it.

A base error carrying a machine-readable `code`, an HTTP `status`, a message, and optional
`details` and `cause`. Then the domain subclasses:

`NotFoundError` · `ValidationError` · `UnauthorizedError` · `ForbiddenError` · `ConflictError` ·
`UnprocessableEntityError` · `TooManyRequestsError` · `InternalError`

**One global handler** — an exception filter in Nest, error middleware in Express and Fastify —
and it is the only place in the codebase that turns an error into an HTTP response. Services
throw; they never build responses.

Rules the handler enforces:

- Anything that is not one of these becomes a **500 with a correlation id**. No stack trace, no
  internal message, no ORM error text leaves the process in production.
- The correlation id appears in the log line **and** in the response body, so a user can quote
  it and you can find it.
- zod failures map to **422** with field-level detail. The validation layer never throws raw.
- **Sentry captures unexpected errors only.** Reporting expected domain errors turns Sentry into
  a log of users mistyping URLs, and the real incident is then invisible inside it.

### Response format

**RFC 9457 problem+json** — `type`, `title`, `status`, `detail`, `instance`, plus `code` and an
`errors[]` array for field-level failures. It is a real standard, it is what enterprise and
government consumers expect, and it gives the frontend exactly one shape to parse.

The frontend reconstructs the same error classes from that body, so a component catches a
`ConflictError` rather than inspecting `err.response.status === 409`.

## Validation

zod, everywhere input crosses the boundary — body, params, query, env. The schema is the
contract, and the same schema is shared with the frontend forms.

## Configuration

A zod schema over `process.env`, parsed once at boot. A missing or malformed variable fails at
startup with a message naming it. Nothing downstream reads `process.env` directly.

## Security

- **helmet** and **rate limiting** — unconditional, neither depends on the shape
- **CORS is conditional on the shape**:

| Shape | CORS |
|---|---|
| Monolith | **None.** The backend serves the built SPA; same origin in production, and Vite's `/api` proxy makes development same-origin too |
| Separated | **Required in production**, allowed origin from env |
| API only / microservice | Only if a browser on another origin calls it. Consumed server-side, off |

- bcrypt for password hashing, when auth is chosen

## Observability

- Structured logging, correlation id on every line
- Sentry, DSN from env, silent when unset
- A health endpoint — containers need one, and so does anything in front of them

## API surface

- **Versioned from day one** — `/v1`. Adding a version to a live API is a migration; starting
  with one is free.
- **Swagger/OpenAPI generated, mounted only outside production.** Guard the mount, not the
  generation.

## Auth

Local, bcrypt. Access token plus optional refresh-token session validation.

Where the refresh token lives is asked, and the two answers are not equivalent: an httpOnly
cookie is unreadable by injected script; `localStorage` is readable by any XSS on the page, and
the refresh token is the long-lived one. Present that when asking, not after.

## RBAC

Enum or tables, per question 6. Either way the enforcement point is a guard, and it reads from
the same place the token was verified — never from the request body.

## Testing

Tests beside the source. `test/` holds configuration only.

Database tests are **fully isolated and truncate between every test**, against the second
Postgres service in the compose file — never the development database.

Truncating is the safe default rather than the fast one. Wrapping each test in a transaction and
rolling back is faster and equally isolated, but breaks the moment the code under test manages
its own transactions, and that failure is confusing. Start with truncate.

## Transports — microservice only

Whatever the answer to question 3, it becomes another service in the compose file, and the
entrypoint changes shape: an HTTP service listens, a broker consumer subscribes. Both still get
the health endpoint, because whatever runs them still needs to know they are alive.
