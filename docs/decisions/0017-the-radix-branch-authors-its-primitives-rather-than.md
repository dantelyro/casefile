# D-017 — The Radix branch authors its primitives rather than shipping them

**Status:** Accepted (2026-08-30).
**Decided by:** dantelyro <beyondmind9@gmail.com> — Grade 2: implied by the branch being offered at
all ("let the user choose radix - manitine - or shacn/ui + tailwind") together with the standing
rule that only versions may not be written by hand. Not asked about directly.

**Implemented by:** `19d9e44` — 2026-08-30.

**Context:** Radix ships behaviour with no appearance. Choosing it means the project needs a set of
styled primitives — button, input, label, textarea, select, card, badge, dialog, sheet, toast,
skeleton, spinner — each a component plus its SCSS module plus a test. No generator emits them.
Mantine and shadcn both avoid this: one is a library, the other has a CLI that copies source in.

**Options:** (a) the plugin carries the primitives as real files under `templates/` and copies them
in; (b) the skill authors them from the pattern documented in `references/frontend-react.md`;
(c) drop the Radix branch and offer only Mantine and shadcn.

**Decision:** (b). (c) contradicts a direct instruction. (a) was not taken **in this change** —
it would make the plugin carry executable source for the first time, and the obvious seed for those
files is a client project, which is not this repo's to publish.

**Trade-offs:** (b) is the branch most exposed to drift: two projects scaffolded months apart get
primitives written twice, and they will not be identical. That is precisely the divergence the
invariants exist to prevent, and this decision accepts it for one branch. It is consistent with the
core principle only because that principle governs *versions*, not authorship — a distinction stated
by the user directly ("the custom part you will make obviously, i dont want is package version
manually built").

**Open, deliberately:** promoting the primitive set to shipped files under `templates/` is the
obvious fix and needs only a source the repo may publish. Until then the plan file must list every
primitive by name, so the user approves the largest block of authored code in any branch before it
is written, not after.
