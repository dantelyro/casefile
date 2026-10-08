# `scaffold.plan.md`

Written at the end of phase 1, before anything touches disk. The user reads it, edits it,
approves it. **Nothing runs until they do.**

## Sections, in order

### 1. Answers

Every question and its answer, including the ones skipped and why. A reader must be able to tell
what was chosen from what was defaulted.

### 2. Repos

What will be created and where. In the separated shape this is two independent git repos — say
both paths.

### 3. Commands

Every command, in execution order, with its exact flags, grouped by repo. Each carries its
recorded verification state.

```
UNVERIFIED  npx @nestjs/cli new api --package-manager npm --skip-git --strict
UNVERIFIED  npm i -D prisma
            npx prisma init --datasource-provider postgresql
```

**No version numbers.** If one appears here, the plan is wrong.

Any command marked `INTERACTIVE` carries the answer sequence that will be driven, inline.

### 4. Written files

Every file the skill will write itself, and **why no generator emits it**. This is the section
that keeps the core principle honest — it should be config and code, never a manifest.

If the Radix branch was chosen, the primitive set is listed here, by name. It is the largest
block of authored code in any branch and the user should see it before approving, not after.

### 5. What this does not do

Named explicitly, because absence is invisible:

- no deploy stage
- no design tokens or themed screens — a separate skill's job
- no CI variables or tokens created — the user creates those, and the plan says which

### 6. Verification

The commands phase 4 will run to prove the scaffold works: build, test suite, `predev` with real
containers and migrations.

## After execution

The plan stays in the repo. It is the record of what was generated and why, and if a generator
fails halfway, resuming is reading a file rather than reconstructing what already happened.
