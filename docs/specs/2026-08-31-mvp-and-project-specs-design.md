# `mvp` and `project-specs` — design

**Date:** 2026-08-31.
**Status:** Design approved in session; not yet implemented.
**Scope:** two new skills, one skill removed. This is a plugin redesign, not an addition.

## Summary

`scaffolding` is dropped. In its place, a cast of actors is dispatched at an idea: a client whose
product it is, domain actors who would use it, and an opinionated dev team who would build it.
They cut the idea down to what is actually worth building first, and emit the specs it is built
from.

| Skill | Takes | Produces |
|---|---|---|
| `mvp` | an idea, as a written brief | `docs/purpose.md`, `docs/requirements.md`, a session record |
| `project-specs` | purpose + requirements | a build plan on disk, with verified generator commands |

`repo-discovery` and `evidence-based-decisions` are untouched.

The first skill is named for what it does rather than how: the output is a defensible MVP — the
smallest thing that serves the purpose — not a review. The cast is the mechanism, and mechanisms
do not belong in names the model matches situations against.

## Why two skills and not one

"What should I actually build first" and "turn that into something buildable" are different
moments, and the `description` is the entire trigger surface. One description matching both fires
the cast when you wanted a scaffold and a scaffold when you wanted a conversation. Two
descriptions, two moments.

The cost is real: the cast is re-briefed at the boundary. Actors in `project-specs` do not remember
the argument they had in `mvp` — they read `purpose.md` and `requirements.md` like anyone else.
That is the price of sharp triggers, and it is mitigated by those two documents being good, which
is the entire point of the first skill.

## What is dropped, and where its parts go

`scaffolding` is 886 lines across `SKILL.md` and eight reference files. Almost none of it is
wasted — it was split along the right seams, just filed under a skill that no longer exists.

| File | Lines | Goes to |
|---|---|---|
| `invariants.md` | 75 | Lives in `project-specs/references/`; also read by `mvp` as actor house style. Already sectioned `Everywhere` / `Backend only` / `Frontend only` / `Scripts` — the first block is carried by every dev actor, the others by their owner. |
| `generators.md` | 194 | Lives in `project-specs/references/`; blocks injected into backend and frontend actor prompts as **equipment**. See "The D-015 problem". |
| `backend.md` | 134 | `project-specs` references, per project type |
| `frontend-react.md` | 91 | `project-specs` references, per project type |
| `frontend-vue.md` | 47 | `project-specs` references, per project type |
| `plan-format.md` | 60 | `project-specs` output format — D-014's plan-on-disk survives intact |
| `questions.md` | 125 | `mvp`, as the brief-building question set |
| `release.md` | 54 | `project-specs` references |
| `SKILL.md` | 106 | Split between the two new `SKILL.md` files |

### The D-015 problem

D-015 says a generator flag set written from memory is a hypothesis about a CLI, which is why every
command in `generators.md` carries `UNVERIFIED`, `INTERACTIVE`, or `no generator`. Deleting
`scaffolding` without a home for that file means the backend actor emits `nest new` with flags it
invented, into a plan you then run. That is the exact failure D-015 exists to prevent, re-entering
through a door this redesign would have built.

**Resolution:** `generators.md` is not a scaffolding artefact, it is equipment. The relevant block
is injected into an actor's prompt at dispatch. The actor chooses *which* generator from its
opinions; the flags come out of a file carrying its own verification state. No actor types a
command from memory, and the verification states stay in one place where they can be promoted as
commands are actually run.

## The cast

Three classes. They answer different questions and are spawned from different sources.

### Client actors — derived from `purpose.md`, count derived from it too

Whose product this is. The client holds the business goal, decides what success means, and is the
only actor with the standing to say **"that is phase two."** For a skill whose output is an MVP,
this is the load-bearing role: the dev team will happily specify everything, and the domain actors
will happily want everything.

The number is not fixed, because it is a property of the purpose. A single-audience tool has one
client. A two-sided marketplace has two whose interests genuinely conflict — the side that wants
listings free and the side that wants them curated — and an MVP that serves only one of them is a
finding worth surfacing before it is built. The count and the roles are read out of `purpose.md`
and proposed with the rest of the roster.

This is why `purpose.md` is drafted in phase 1, before any dispatch: the client cast cannot be
derived until there is a stated purpose to derive it from.

### Dev team — fixed, always spawned

Not neutral reviewers. Opinionated senior specialists with a house style, which is what makes their
output consistent across projects rather than a fresh set of preferences every run.

| Actor | Hunts for | Standing opinions |
|---|---|---|
| `architect` | Boundaries, the core entity, what talks to what | — |
| `backend` | Storage, state, sync, API shape | TypeScript always, no `any`, prefers classes; the `Backend only` invariants |
| `frontend` | Flows, screens, what the user cannot do yet | React; customizable component set; also UX/UI, drafts the design direction |
| `qa` | "How would I test that?" — kills unfalsifiable requirements | — |
| `security` | Authn/authz, ownership, data exposure | — |

Every dev actor carries the `Everywhere` invariant block. Rejected: an eight-role team adding
product, DevOps and UX — product overlaps the client actors, UX overlaps the frontend actor, and
deployment gaps do not exist yet at the idea stage.

**The frontend actor and D-016.** It drafts the design direction in text — tokens, component set,
and the theme seams D-016 already named (`shared/theme/tokens.scss`, Mantine CSS variables,
`quasar.variables.scss`, `tailwind.config`). It does **not** absorb the design-system skill. D-016's
reasons stand: that skill needs a browser and an interaction round-trip, and it is useful on
projects that already exist, which no day-zero skill can be. The actor writes the brief it renders.

### Domain actors — derived from the brief

Two or three, deliberately chosen to disagree: for a hunting site, a weekend bowhunter, a
commercial guide and a public-land elk hunter want three different applications. Agreement is a
candidate core requirement; divergence is scope to cut or make configurable.

Distinct from the client: the client owns the product, domain actors live in the world it is for.
They are frequently in tension, and that tension is the most useful thing the skill produces — the
client wants the feature that closes a sale, the domain actor wants the one that works with cold
hands at 5am.

The full roster is **proposed and approved before any dispatch** — the same gate D-014 puts on
`scaffold.plan.md`, for the same reason: a bad cast is cheaper to reject than to read the output of.

## Mechanism

Actors are not agent definition files. Each is a system prompt assembled at runtime — role,
standing opinions, the invariant blocks it owns, and any equipment it needs — passed as the
`prompt` of an `Agent` dispatch. Nothing is registered, nothing is written to `.claude/agents/`, no
restart is involved. That is what lets the client and domain casts be generated per idea.

1. **Write the brief.** One paragraph, on disk, from the `questions.md` set. Every actor receives
   exactly this text. The brief is the ceiling on output quality, so it is shown to the user before
   anything dispatches.
2. **Draft `purpose.md`.** From the brief. Needed before the roster, because the client cast is
   derived from it.
3. **Propose the roster** — clients, dev team, domain actors, with one line on why each is present
   and why there are that many clients. Wait for approval.
4. **Round 1 — parallel, blind.** All actors at once. None sees another's answer.
5. **Synthesize.** Contradictions, undecided questions, single-source claims.
6. **Round 2 — targeted.** Re-dispatch *only* actors in a contradiction, each shown the other's
   position, asked to resolve or hold. A coherent brief costs nothing here.
7. **Cut to an MVP, refine `purpose.md`, write the documents.**

### Why this and not a round table

Rejected: a shared thread where all actors see every message and argue to convergence. It produces
better answers — it kills a wrong call from the architect in one exchange instead of letting it
propagate, and it finds gaps that exist only in the team's *own* proposals rather than in the brief.

Two things ruled it out. Actors in a shared thread converge socially: an objection is dropped after
one push-back, and the transcript cannot distinguish a conceded argument from an agreeable model.
For a skill whose product is a defensible cut, a mechanism that manufactures agreement attacks the
deliverable. And the orchestration — spawn, feed each the others' positions, loop, cap the rounds —
is hand-rolled and the most breakable thing in the skill, against a design that is N parallel
dispatches and a synthesis pass.

**Accepted limitation, recorded so it is not rediscovered as a bug:** blind actors find gaps in the
brief only. A gap that appears once `backend` has proposed permission inheritance — which
`security` would catch on seeing it — is missed. Round 2 recovers some, but only where synthesis
already spotted a contradiction to chase.

## Evidence classes

Tagged by **claim type, not by who said it** — a client actor reasoning about your stated purpose
and a client actor inventing a market fact produce different things, and one actor emits both.

- **`[reasoned]`** — an inference from the brief, `purpose.md`, or another actor's stated position.
  "Your purpose says weekend hunters, this feature only serves guides." "You have no story for who
  owns a shared trip log." The reasoning is in the output; you verify it by reading it.
- **`[claimed — UNVERIFIED]`** — an assertion about the world outside your documents. "Hunters have
  no signal in the field." "Nobody pays more than $10 a month for this." Grade 4 on the ladder in
  `evidence-based-decisions`, a hypothesis from a machine that has never been hunting and has never
  sold anything. Quarantined in its own section, never merged into the requirement list, carrying an
  explicit instruction to confirm with a real human before anything is designed around it.

Domain actors emit mostly `claimed`, the dev team mostly `reasoned`, clients a mix — which is why
the tag goes on the claim.

A `claimed` line that survives contact with a real person is promoted by hand, and the promotion is
a decision-log entry with its new grade.

## Output of `mvp`

**`docs/purpose.md`** — drafted in phase 2 from the brief, refined in phase 7 once the cast has
spoken. The pain, who has it, the non-goals. Written early because the client cast and the actors
need something to argue against; polished late because that argument is what sharpens it.

**`docs/requirements.md`** — `F-NN` functional and `N-NN` non-functional, per D-011, with a number
on every non-functional one. Each line attributed to the actor that raised it and tagged with its
claim type. Split into **in the MVP** and **cut, with the reason and who wanted it** — a cut
requirement with its advocate named is what stops the same argument being had again in six weeks.
`UNVERIFIED` claims are held separately and never mixed in.

**`docs/discovery/YYYY-MM-DD-<topic>.md`** — the session record: the brief verbatim, the cast and
why, what clashed and how round 2 resolved it, what is still undecided, and the unverified claims.
Distilled, not dumped — a full cast's raw round-1 prose is thousands of lines read once. It exists
as the sourcing behind every requirement line.

Nothing is written unasked. The skill offers and waits; no devflow skill creates a document in a
project that has not agreed to it.

## Output of `project-specs`

A build plan on disk before any command runs, in the `plan-format.md` shape D-014 established:
every command with its flags, listed, approved before execution, resumable by reading the file
after a half-failed run. Commands come from `generators.md` with their verification states intact.

## Interlock with `evidence-based-decisions`

That skill is the spine of the plugin, not a downstream consumer, and it is a generator in its own
right — its "No docs yet" path creates the doc set, and its loop writes decision entries. The line
between it and the new skills is therefore **not** creator versus custodian. It is what gets
created: `evidence-based-decisions` generates and maintains the *reasoning record*;
`project-specs` generates the *repository*. Four seams follow from that.

**The seeding path splits, and the split is itself evidence-graded.** Today its "No docs yet:
propose, then ask" path covers every case. It should not. Seeding `purpose.md` from a repo that
already has code is reading real evidence — layout, stack, entry points, Grade 1 and 2. Seeding it
from a cast of actors is Grade 4 until a human confirms it. Different acts, different owners:

- **Code exists, docs do not** → `evidence-based-decisions` keeps its current path unchanged. Seed
  from what the repo shows. The code is better evidence than any actor, and always will be.
- **No code, no docs** → `mvp`. There is nothing to read, so a cast is the best available source,
  and everything it produces carries its claim type.

`mvp` hands back for the parts that skill already owns — setting the initial watermark to `HEAD`,
and seeding `docs/decisions/`. `mvp` must not restate the log format or the entry template; those
live in `references/decision-log.md` and stay there (D-008).

**`docs/discovery/` joins the doc set** in `living-documents.md`, which already tables purpose and
requirements with when to read each. The session record has a job none of the others have: it is
the only document saying *why a requirement exists and who wanted it*, which is exactly what a
future reader needs before deleting one.

**Requirements rot fastest** — D-011 says so outright. That makes them the document the
session-start replay matters most for: a commit that changes behaviour invalidates an `F-NN` line
silently, and nothing else in the repo will notice.

**The `UNVERIFIED` backlog is its business.** Every `[claimed — UNVERIFIED]` line is a Grade 4
hypothesis parked in a project document. Confirming one with a real person is a promotion, and a
promotion is a decision entry carrying its new grade — the loop that skill already runs. Without
that handoff the quarantine section is a list nobody revisits, which is D-011's rot with extra
labelling on top.

## Placement

```
skills/mvp/
  SKILL.md              principles, the two claim types, the seven phases
  references/
    clients.md          deriving the client cast and its size from purpose.md
    dev-team.md         the five actor prompts, standing opinions, invariant blocks
    domain-actors.md    deriving a cast from a brief; disagreement by design
    brief.md            the question set (from scaffolding/questions.md)
    synthesis.md        finding contradictions; when round 2 is worth dispatching
    documents.md        purpose.md, requirements.md and the session record formats

skills/project-specs/
  SKILL.md              phases, the plan gate
  references/
    generators.md       verified commands, verification states preserved
    invariants.md       the house style, as written output rather than actor opinion
    backend.md  frontend-react.md  frontend-vue.md  plan-format.md  release.md
```

`generators.md` and `invariants.md` are read by both skills — `project-specs` writes from them,
`mvp` injects blocks of them into actor prompts. One copy, in `project-specs/references/`,
referenced by path from `mvp`. Within one plugin that is fine; D-016 forbids depending on *another*
plugin's cache directory, not on your own files.

**No `model` in either frontmatter.** D-012 records that a skill's `model` override applies for the
rest of the turn, not only while the skill runs. Actor cost is set per dispatch instead, where it
belongs: dev-team actors on the session model, client and domain actors on Sonnet, since role-play
is cheaper work than architectural critique.

## Triggers

`mvp` fires on: a new project idea about to be built, "what should I build first", "what am I
missing", a feature set nobody has challenged, an empty or absent `requirements.md`, and `/init` in
a directory with no project in it. It must **not** fire on adding a feature to a project whose
requirements exist.

`project-specs` fires on: "scaffold this", "set up the repo", a `requirements.md` that exists with
no code beside it, and adding a frontend or backend next to an existing one.

Ordering: idea → `mvp` gives it form and fills the doc set → `project-specs` builds it →
`evidence-based-decisions` keeps it honest. `repo-discovery` is orthogonal — it answers what an
existing project is. State the ordering once, in `mvp/SKILL.md`, nowhere else (D-008).

## Decisions to record on implementation

- **The cast replaces the scaffolder.** `scaffolding` is dropped and its references redistributed.
  Supersedes D-013 (`scaffolding` runs before `/init`) — `/init` in an empty directory is now
  `mvp`'s trigger. D-014 (plan on disk) and D-015 (verification states) survive, relocated to
  `project-specs`.
- **Three actor classes, and the client count is derived from purpose.** Records why the client is
  separate from the domain actor, and why the number is not fixed.
- **Parallel plus targeted follow-up, over a round table.** The argument above is the entry: the
  round table produces better answers and was rejected anyway. That is precisely the reasoning that
  gets lost and then re-litigated.
- **The frontend actor drafts the design direction; D-016 stands.** Records that absorbing the
  design-system skill was considered and refused, and why.

- **The seeding path splits by evidence grade.** `evidence-based-decisions` keeps the case where
  code exists; `mvp` takes the empty directory. Records why, since the obvious reading — "`mvp`
  seeds documents now" — is wrong and would delete the better path.

## Files outside the new skills that change

- `skills/evidence-based-decisions/SKILL.md` — the "No docs yet" section splits and delegates the
  empty-directory case to `mvp`.
- `skills/evidence-based-decisions/references/living-documents.md` — `docs/discovery/` joins the
  doc-set table.
- `README.md` — the skill table, the "the three compose" paragraph, and the layout tree all name
  `scaffolding`. Three skills become four.
- `CLAUDE.md` — the architecture section states `scaffolding`'s precedence over `/init` and the
  plan-on-disk rule; both move to the new owners. Reconciliation watermark moves in the same commit.
- `.claude-plugin/plugin.json` and `marketplace.json` — minor version bump, and the duplicated
  `description` changes in both together if it enumerates the skills.

## Staging

Build in this order so there is never a gap with no working path:

1. **`mvp`**, together with the `evidence-based-decisions` seeding split — the two are one change.
   Shipping `mvp` without the split leaves two skills claiming the same empty directory.
2. **`project-specs`** — needs `scaffolding`'s reference files, which still exist at this point, so
   the migration is a move rather than a rewrite.
3. **Delete `scaffolding`**, once `project-specs` covers it.
4. **Docs sweep** — `README.md`, `CLAUDE.md`, `living-documents.md`, and the watermark, which moves
   in the same commit as the doc update so it always names a commit whose docs were true.

Each of the four is a shippable state with a version bump. Stopping after any of them leaves the
plugin coherent, which is the property that makes the ordering worth following.
