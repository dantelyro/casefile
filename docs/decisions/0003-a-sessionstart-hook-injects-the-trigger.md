# D-003 — A SessionStart hook injects the trigger a description cannot match

> **Reconstructed entry (2026-08-27).** The reasoning is read almost verbatim from the author's
> own comments — the README section "Why there is a hook" and the header comment in
> `hooks/session-start`. Both were written with the change, so this is the author's reasoning
> rather than an inference; only the options list is reconstructed.

**Status:** Accepted (2026-08-19).
**Decided by:** dantelyro <beyondmind9@gmail.com> — resolved by blaming `2a2476b`, the `feat`
commit that added `hooks/`.
**Implemented by:** `2a2476b` — 2026-08-19.

**Context:** A skill fires when the model recognises its `description` in the situation in front
of it. That mechanism works for `repo-discovery`, whose triggers are things a person types —
*where does X live*, *how do I run this*. It cannot work for `evidence-based-decisions`: its
primary trigger is **the start of a session**, which no first message ever states, and its other
triggers are facts about the repo — a decision log exists, the docs are behind `HEAD` — which
cannot be recognised before reading the repo, and reading the repo is what the skill is for.

**Options:** (a) leave it to the description and accept that the session-start path never fires;
(b) instruct users to type `/evidence-based-decisions` at the start of every session; (c) emit a
`SessionStart` hook that names the skill and tells the model to invoke it.

**Decision:** (c), matched on `startup|clear|compact` so it survives a context clear as well as a
cold start. The directive states what the skill will have the model do, so the injection reads as
an offer rather than an unexplained order.

**Trade-offs:** Every session in every project with the plugin enabled now pays a fixed context
cost and takes an orientation step it did not ask for — mitigated by D-004 and by the skill's own
"neither applies — say so in one line" exit, but not eliminated. The hook also makes the plugin
depend on a working shell (see D-005).

**The wider lesson, which outlives this entry:** a skill whose trigger is a fact about the world
rather than a phrase in the prompt has no way to fire on its own. Hooks are where those triggers
live.
