# The work branch

Used by `implement` and `fix-bug`. A milestone or a bug fix lands on one branch of its own; the
developer merges it into the default branch (`.claude/casefile.json`, else `main`) when they choose,
and drops it by deleting the branch (D-062). You never merge it into the default branch.

1. **Name it with the developer.** Propose a name — `feat/<milestone>-<slug>` for a milestone
   (`feat/m7-saved-jobs`), `fix/<issue id>-<slug>` for a bug (`fix/i-0007-upload-keeps-file`) — and
   ask with the AskUserQuestion tool: your proposal first, two alternatives after it; the tool's own
   free-text answer is the developer's name. The name is how they keep track of what they are working
   on, so never pick it alone.
2. **Create it** with a clean working tree: a milestone from the default branch; a fix from the branch
   the bug is on — the default branch, or the `feat/` branch whose work holds it. `git switch -c
   <name> <from>`. Already on a `feat/` or `fix/` branch for this same work (resuming) → stay on it,
   nothing to ask.
3. **Siblings** (`siblings` in `.claude/casefile.json`): the same name, created the same way in each
   sibling, from its default branch, only while its working tree is clean; otherwise stop and tell
   the developer.
4. **Issue and decision numbers** come from the files on the current branch, so two open branches can
   hand out the same number. Before the developer merges, check the default branch for a clash
   (`git ls-tree --name-only <default> docs/issues/ docs/decisions/`) and say so.

Never merge the work branch into the default branch and never push it: both are the developer's.
When the work is done, say the branch is ready for them to merge.
