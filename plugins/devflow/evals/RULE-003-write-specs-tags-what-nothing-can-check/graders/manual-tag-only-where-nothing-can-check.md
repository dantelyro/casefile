---
type: llm
---

The final reply shows a draft of specs. It passes only if all three hold. (1) The rule about how the
welcome screen feels (calm and friendly) is tagged [MANUAL]. (2) The rule that the save button stores
the job in the database and the rule that the onboarding skill greets the user by name are NOT tagged
[MANUAL] (a test checks the first, an eval checks the second). (3) No rule is tagged as critical
without asking: either the draft tags nothing critical, or it only suggests a rule might be critical
and asks the developer, tagging it only on a yes.
