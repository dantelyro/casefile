# D-010 — Watermark extraction uses POSIX `sed` and guards the empty case

**Status:** Accepted (2026-08-27).
**Decided by:** dantelyro <beyondmind9@gmail.com> — the defect was found while implementing D-009
and fixed in the same session; the call to fix it here rather than defer it follows the skill's
own "correct a false claim immediately" rule.
**Implemented by:** `30f026b` — 2026-08-27.

**Context:** Grade 1 evidence — the documented command was run against this repo and failed:

```
$ grep -oP 'reconciled through:\s*`\K[0-9a-f]+' CLAUDE.md
grep: -P supports only unibyte and UTF-8 locales
```

`-P` is a GNU extension, and Git Bash on Windows with an unset `LANG` rejects it. That is the
smaller half of the defect. The larger half is what happened next: `$WM` was empty, and
`git log --oneline ""..HEAD -- <paths>` is **not an error** — both sides of an empty range
default to `HEAD`, so it printed nothing. Nothing is exactly what an up-to-date repo prints. The
broken command reported the docs as current.

**Options:** (a) keep `grep -oP` and note the locale caveat in the recovery table; (b) switch to
`grep -oE` plus a `cut`, portable but two processes and a fragile field index; (c) POSIX `sed`
with a backreference, plus an explicit `[ -z "$WM" ]` branch before the replay.

**Decision:** (c). The empty-case guard is the part that matters — a portable extractor still
fails silently on a document that simply has no watermark, which is the common case in a repo
being reconciled for the first time. The `DOC` variable is lifted out of the command so the
project-instructions location from D-009 is a one-word change.

**Trade-offs:** The snippet grew from two lines to nine, in a reference file that D-008 has just
finished compressing. Accepted: a four-line command that lies is worse than a nine-line one that
does not.

**The wider lesson, which outlives this entry:** this is the skill's own Grade 4 rung — a
conclusion drawn from the absence of an error — reached by a command *in the skill*. A check
whose failure mode is indistinguishable from its success mode is not a check. Test the extraction
before trusting the comparison.
