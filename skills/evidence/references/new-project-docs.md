# New project docs

What to do when a project has no context documents yet, or keeps them in the old
`mental-model.md` format. Each happens once per project, which is why it is not in `SKILL.md`.

## A `mental-model.md` is replaced without asking

Write `docs/architecture/overview.md` from the code in the architecture overview's format, keeping
what the old file says that is still true, delete `mental-model.md`, repoint every link to it, and
set the watermark to `HEAD` — one commit. The developer decided this (D-050); the old format told
readers nothing useful.

## No docs yet: propose, then ask

A project with no project instructions, architecture document or decision log may keep this
material elsewhere, or want none of it. Say what each file is for and what it costs, and wait
for an answer — files nobody wanted are worse than no files.

**Two cases, and the split is itself an evidence grade.**

- **Code exists, docs do not.** Seed from what the repo shows — layout, stack, entry points. That
  is Grade 1 and 2 evidence, and it beats any actor's account of what the project probably is.
- **No code, no docs.** There is nothing to read, so nothing here can be seeded with evidence.
  Ask the developer what the project is, and offer the `write-specs` skill to turn the answer
  into specs, before creating anything.

Seeding an empty directory from this skill would describe a project from nothing, which is the
mistake this entire skill exists to prevent.

**Run `/init` first.** Project instructions come before the rest of the set: they are the only
document every session loads, so a log created without them is a log nothing points at. Then
`docs/purpose.md` — what the project is for — before the architecture document, which describes a
shape that only makes sense once that is settled.

**`docs/requirements.md` is never seeded here**, on either branch. Layout, stack and entry points
are observable on disk; a `must` is not. Code shows what a system does, never what it is obliged to
do, so reading a requirement off an implementation is Grade 4. Requirements come from the people
who decide them, never from this skill.

Once accepted, seed from what the repo already shows — layout, stack, entry points — set the
initial watermark to `HEAD`, and start the log as `docs/decisions/NNNN-slug.md`, one decision
per file, with a generated `docs/decisions/README.md` index. `decisions/` sits **beside**
`architecture/`: the architecture document says what exists and where, the log says why and
what was given up, and the log covers scope and product choices no architecture document
describes. Both the layout and the placement are fixed from entry one.

An empty log with a numbering convention is the correct starting state; invent no decisions to
fill it. Every seeded entry is a **reconstruction**: mark it as one, and resolve `Decided by`
by blaming the `feat`/`fix` commit that implemented the change. Whoever asked you for the
documentation is rarely whoever made the call, and the entry reads as first-hand either way.
