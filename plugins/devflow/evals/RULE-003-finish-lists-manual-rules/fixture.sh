#!/usr/bin/env bash
# A milestone whose every task is done: one tested rule, one [MANUAL] rule, one [VERIFY] rule.
set -e
git init -q -b main
git config user.email eval@example.com
git config user.name eval
mkdir -p .claude src tests docs/specs docs/plans docs/product
cat > .claude/devflow.json <<'EOF'
{
  "build_order": "docs/product/blueprint.md",
  "default_branch": "main",
  "apps": {
    "app": {
      "path": ".",
      "test": "python -c \"pass\""
    }
  }
}
EOF
printf '{\n  "worktree": {"baseRef": "head"}\n}\n' > .claude/settings.json
printf 'def save(job):\n    return job\n' > src/jobs.py
printf 'def test_JOBS_010_a_saved_job_is_kept():\n    pass\n' > tests/test_jobs.py
cat > docs/specs/README.md <<'EOF'
# Specs

The ID is the area's prefix and a three-digit number. A rule needs no tag. Tags: `[LATER]`, `[VERIFY]`, `[MANUAL]`.

## Files

| File | What |
|---|---|
| [14-jobs.md](14-jobs.md) | Saved jobs |
EOF
cat > docs/specs/14-jobs.md <<'EOF'
# Jobs

### JOBS-010 · A saved job is kept

```
Given a job
When the user saves it
Then it is kept
```

### JOBS-011 · The saved page feels calm [MANUAL]

```
Given the saved page
When the user opens it
Then it feels calm
```

### JOBS-012 · Jobs sync with the partner API [VERIFY]

```
Given the partner API
When jobs are saved
Then they sync (the API's rate limit is unconfirmed)
```
EOF
cat > docs/product/blueprint.md <<'EOF'
# Jobs app

## Build order

- **M1 — Setup** (0.1.0): none.
- **M2 — Saved jobs** (0.2.0): JOBS-010, JOBS-011, JOBS-012.
EOF
cat > docs/plans/M2.md <<'EOF'
# Plan: M2 Saved jobs
Planned: 2026-10-01

Scope (build order): M2 — Saved jobs: JOBS-010, JOBS-011, JOBS-012.

## Tasks
### T1 · Saving a job keeps it
- Status: done (abc1234)
- Rules: JOBS-010
- App: app
- Test first: tests/test_jobs.py — test_JOBS_010_a_saved_job_is_kept
- Then implement: src/jobs.py, tests/test_jobs.py
- Done when: `python -c "pass"` exits 0
- Depends on: none
- Parallel-safe with: none

### T2 · The saved page
- Status: done (def5678)
- Rules: JOBS-011
- App: app
- Test first: none (no test: how the page feels, which the developer checks by hand)
- Then implement: src/jobs.py
- Done when: `python -c "pass"` exits 0
- Depends on: T1
- Parallel-safe with: none

## Rules covered
- JOBS-010 → T1
- JOBS-011 → T2
EOF

git add -A && git commit -qm init
